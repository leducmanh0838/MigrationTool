# --- MigrationService.py (Quản lý phiên chạy) ---
import json
import traceback

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


class MigrationService:
    def __init__(self, write_connector: BaseWriteConnector, read_connector: BaseReadConnector,
                 migration_id=None,
                 migration_path: list = None):
        # 1. Kiểm tra ràng buộc: Chỉ cho phép truyền 1 trong 2
        if (migration_id is not None) and (migration_path is not None):
            raise ValueError("Chỉ được truyền 'migration_id' HOẶC 'migration_path', không được truyền cả hai.")

        if (migration_id is None) and (migration_path is None):
            raise ValueError("Phải truyền ít nhất 'migration_id' hoặc 'migration_path'.")

        # self.migration_path = migration_path
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

        # 1. Khởi tạo Dữ liệu/Service cho phiên chạy mới
        migration_context = {
            "migration_id": self.migration_id,
        }
        # Nếu có checkpoint_source_entity_name thì chỉ chạy từ thời điểm đó
        if self.checkpoint_source_entity_name and self.checkpoint_source_entity_name in self.migration_path:
            idx = self.migration_path.index(self.checkpoint_source_entity_name)
            self.migration_path = self.migration_path[idx:]

        for entity in self.migration_path:
            is_load_more = True
            current_page = 1
            if entity == self.checkpoint_source_entity_name:
                current_page = self.checkpoint_source_entity_page

            while is_load_more:
                is_load_more = self._migrate_data_batch(entity, current_page, migration_context)
                current_page += 1
                with get_db() as db:
                    dao = MigrationDAO(db)
                    dao.update_record(
                        id=self.migration_id,
                        checkpoint_source_entity_page=current_page,
                        checkpoint_source_entity_name=entity,
                    )

    def _migrate_data_batch(self, entity, current_page, migration_context) -> bool:
        entity_source_data, is_load_more = self.read_connector.get_entity_batch(entity, page=current_page)
        mapper = self.entity_mappers.get(entity)
        for source_record in entity_source_data:
            # 1. Check exit source id
            try:
                with get_db() as db:
                    dao = IdMappingDAO(db)
                    exit = dao.exists_by(
                        entity_name=entity,
                        source_entity_id=source_record.get(mapper.primary_source),
                        migration_id=self.migration_id
                    )
                    if exit:
                        continue
                # 2. Bước Validate
                is_valid, validated_record = mapper.validate_record(source_record)

                if is_valid:
                    # 3. Bước Ánh xạ (sử dụng current_id_map của phiên chạy)
                    target_data = mapper.to_record_target(
                        validated_record,
                        context=migration_context
                    )
                    # 4. Bước Ghi vào đích (WooCommerce)
                    created_target_record = self.write_connector.create_entity(entity, target_data)
                    # 5. Write id mapping
                    with get_db() as db:
                        dao = IdMappingDAO(db)
                        dao.create_record(
                            entity_name=entity,
                            source_entity_id=source_record.get(mapper.primary_source),
                            target_entity_id=created_target_record.get(mapper.primary_target),
                            migration_id=self.migration_id
                        )
            except Exception as e:
                reason = str(e) if str(e) else type(e).__name__
                error_details = traceback.format_exc()
                raw_data_json = json.dumps(source_record)

                with get_db() as db:
                    dao = DeadLetterQueueDAO(db)
                    dao.create_record(
                        entity_name=entity,
                        # source_entity_id=source_entity_id,
                        reason=reason[:50],
                        error_details=error_details,
                        raw_data_json=raw_data_json,
                        migration_id=self.migration_id,
                    )
        return is_load_more


if __name__ == "__main__":
    # magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)
    # data, is_load_more = magento_connector.get_entity_batch("customer", page_size=30, page=2)

    magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)

    woo_connector = WooCommerceConnector(WordPressConfig.BASE_URL, WordPressConfig.USERNAME,
                                         WordPressConfig.PASSWORD)

    a, b = woo_connector.check_connection()
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
