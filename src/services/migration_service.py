# --- MigrationService.py (Quản lý phiên chạy) ---
import json
import traceback
import time

from config.settings import MagentoConfig, WordPressConfig
from src.connectors.read_connectors.magento_connector import MagentoConnector
from src.connectors.abstract.base_read_connector import BaseReadConnector
from src.connectors.write_connectors.woocommerce_connector import WooCommerceConnector
from src.connectors.abstract.base_write_connector import BaseWriteConnector
from src.database.dao.dlq_dao import DeadLetterQueueDAO
from src.database.dao.id_mapping_dao import IdMappingDAO
from src.database.dao.migration_dao import MigrationDAO
from src.database.session import get_db
from src.mappers.entity_migration_mapper import EntityMigrationMapper
from src.ui_handlers.abstract.base_migration_ui_handler import BaseMigrationUIHandler
from datetime import datetime, timezone


class MigrationService:
    def __init__(self, write_connector: BaseWriteConnector, read_connector: BaseReadConnector,
                 migration_id=None,
                 migration_path=None, ui_handler: BaseMigrationUIHandler = None):
        # 1. Kiểm tra ràng buộc: Chỉ cho phép truyền 1 trong 2
        if migration_id:
            migration_path = None
        elif migration_path is None:
            migration_path = ['category', 'product', 'customer', 'order']

        # self.migration_path = migration_path
        self.ui_handler = ui_handler or BaseMigrationUIHandler()

        self.source = read_connector.get_platform_name()
        self.target = write_connector.get_platform_name()

        self.write_connector = write_connector
        self.read_connector = read_connector

        self.migration_path = migration_path or []
        self.checkpoint_source_entity_page = None
        self.checkpoint_source_entity_name = None
        self.migration_id = migration_id

        with get_db() as db:
            dao = MigrationDAO(db)
            if migration_id:
                migration = dao.get_by_id(migration_id)
                if migration:
                    # Ưu tiên lấy path từ DB để đảm bảo tính nhất quán của phiên làm việc cũ
                    self.migration_path = migration.entity_path or self.migration_path
                    self.checkpoint_source_entity_page = migration.checkpoint_source_entity_page
                    self.checkpoint_source_entity_name = migration.checkpoint_source_entity_name
            else:
                # Tạo migration mới và lưu vào DB
                migration = dao.create_record(source_platform=self.source,
                                              target_platform=self.target,
                                              entity_path=self.migration_path)
                self.migration_id = migration.id

        self.entity_mappers = {
            entity: EntityMigrationMapper(self.source, self.target, entity) for entity in self.migration_path
        }

    def run_migration(self):
        self.ui_handler.info(f"Bắt đầu migrate từ {self.source} sang {self.target}...")

        migration_context = {"migration_id": self.migration_id}
        summary_data = []  # Để in bảng tổng kết cuối cùng

        # Xử lý Checkpoint nếu có
        path_to_run = self.migration_path
        if self.checkpoint_source_entity_name and self.checkpoint_source_entity_name in path_to_run:
            idx = path_to_run.index(self.checkpoint_source_entity_name)
            path_to_run = path_to_run[idx:]
            self.ui_handler.warning(
                f"Tiếp tục từ checkpoint: {self.checkpoint_source_entity_name} (Page: {self.checkpoint_source_entity_page})")

        updated_at_from = None
        updated_at_to = datetime.now(timezone.utc)
        with get_db() as db:
            dao = MigrationDAO(db)
            migration = dao.get_by_id(id=self.migration_id)
            if self.checkpoint_source_entity_name and self.checkpoint_source_entity_page:
                # if migration.checkpoint_source_updated_at:
                updated_at_to = migration.checkpoint_source_updated_at
            else:
                updated_at_from = migration.checkpoint_source_updated_at
                dao.update_record(self.migration_id, checkpoint_source_updated_at=updated_at_to)
        for entity in path_to_run:
            start_time = time.time()
            total_count = self.read_connector.get_entity_count(entity, updated_at_from=updated_at_from,
                                                               updated_at_to=updated_at_to)
            success_count = 0
            error_count = 0

            # Khởi tạo Progress Bar cho từng Entity
            with self.ui_handler.track_progress(entity.capitalize(), total_count) as progress:
                task = progress.add_task("migrating", total=total_count)

                is_load_more = True
                current_page = 1
                if entity == self.checkpoint_source_entity_name:
                    current_page = self.checkpoint_source_entity_page

                while is_load_more:
                    # Gọi batch và lấy kết quả đếm
                    batch_success, batch_error, is_load_more = self._migrate_data_batch(
                        entity, current_page, updated_at_from, updated_at_to, migration_context
                    )

                    success_count += batch_success
                    error_count += batch_error

                    # Cập nhật thanh tiến trình
                    progress.update(task, advance=(batch_success + batch_error))

                    # Lưu checkpoint vào DB
                    current_page += 1
                    with get_db() as db:
                        dao = MigrationDAO(db)
                        dao.update_record(
                            id=self.migration_id,
                            checkpoint_source_entity_page=current_page,
                            checkpoint_source_entity_name=entity,
                        )

            # Báo cáo kết quả sau mỗi Entity
            duration = round(time.time() - start_time, 2)
            summary_data.append({
                "name": entity.capitalize(),
                "total": total_count,
                "current": success_count,
                "errors": error_count,
                "time": duration
            })

            if error_count > 0:
                self.ui_handler.warning(f"Thực thể {entity} hoàn tất với {error_count} lỗi.")
            else:
                self.ui_handler.success(f"Thực thể {entity} hoàn tất 100%.")

        with get_db() as db:
            dao = MigrationDAO(db)
            dao.update_record(id=self.migration_id,
                              is_completed=True,
                              checkpoint_source_entity_page=None,
                              checkpoint_source_entity_name=None)

        self.ui_handler.finish_migration(summary_data)

    def _migrate_data_batch(self, entity, current_page, updated_at_from, updated_at_to, migration_context) -> tuple:
        entity_source_data, is_load_more = self.read_connector.get_entity_batch(entity, page=current_page,
                                                                                updated_at_from=updated_at_from,
                                                                                updated_at_to=updated_at_to)
        mapper = self.entity_mappers.get(entity)

        success_in_batch = 0
        error_in_batch = 0

        for source_record in entity_source_data:
            try:
                # 1. Check tồn tại
                source_id = source_record.get(mapper.primary_source)
                with get_db() as db:
                    dao = IdMappingDAO(db)
                    if dao.exists_by(entity_name=entity, source_entity_id=source_id, migration_id=self.migration_id):
                        # Nếu đã tồn tại, tính là thành công (đã xử lý) và bỏ qua
                        success_in_batch += 1
                        continue

                # 2. Validate & Map
                is_valid, validated_record = mapper.validate_record(source_record)
                if is_valid:
                    target_data = mapper.to_record_target(validated_record, context=migration_context)

                    # 3. Write Target
                    created_record = self.write_connector.create_entity(entity, target_data)

                    # 4. Save Mapping
                    with get_db() as db:
                        dao = IdMappingDAO(db)
                        dao.create_record(
                            entity_name=entity,
                            source_entity_id=source_id,
                            target_entity_id=created_record.get(mapper.primary_target),
                            migration_id=self.migration_id
                        )
                    success_in_batch += 1
                else:
                    error_in_batch += 1

            except Exception as e:
                error_in_batch += 1
                # Lưu lỗi vào DLQ (Dead Letter Queue)
                reason = str(e) or type(e).__name__
                with get_db() as db:
                    dao = DeadLetterQueueDAO(db)
                    dao.create_record(
                        entity_name=entity,
                        reason=reason[:50],
                        error_details=traceback.format_exc(),
                        raw_data_json=json.dumps(source_record),
                        migration_id=self.migration_id,
                    )

        return success_in_batch, error_in_batch, is_load_more


if __name__ == "__main__":
    # magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)
    # data, is_load_more = magento_connector.get_entity_batch("customer", page_size=30, page=2)

    magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)
    # print(magento_connector.get_entity_batch("product"))
    # print(magento_connector.get_entity_count("product"))
    # print(magento_connector.get_entity_count("category"))
    # print(magento_connector.get_entity_count("customer"))
    # print(magento_connector.get_entity_count("order"))
    #       base_url: http://localhost:8000/
    #       wq_password: leducmanh0838@gmail.com
    #       wq_username: oVvY wL2n XrIs 27ke VJug HVhJ
    woo_connector = WooCommerceConnector(WordPressConfig.BASE_URL, WordPressConfig.USERNAME,
                                         WordPressConfig.PASSWORD)
    # woo_connector.flush_all_data_in_entity(entity_name='product', ids=[4013, 4006])
    # a, b = woo_connector.check_connection()
    # print(a, b)
    # service = MigrationService(
    #     # schema_mapper=schema_manager,
    #     migration_path=['category', 'product', 'customer', 'order'],
    #     # migration_path=['category', 'product'],
    #     # migration_id=11,
    #     read_connector=magento_connector,
    #     write_connector=woo_connector,
    # )
    #
    # service.run_migration()
