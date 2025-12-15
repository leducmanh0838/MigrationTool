# --- MigrationService.py (Quản lý phiên chạy) ---
import json

from src.connectors.read_connectors.read_base_connector import ReadBaseConnector
from src.connectors.write_connectors.write_base_connector import WriteBaseConnector
from src.mappers.entity_migration_mapper import EntityMigrationMapper


class MigrationService:
    def __init__(self, migration_path: list, write_connector: WriteBaseConnector, read_connector:ReadBaseConnector):
        # Khởi tạo MigrationService 1 LẦN duy nhất
        self.migration_path = migration_path  # ["category", "product"]
        self.source = read_connector.get_platform_name()
        self.target = write_connector.get_platform_name()
        self.write_connector = write_connector
        self.read_connector = read_connector
        self.entity_mappers = {
            entity: EntityMigrationMapper(self.source, self.target, entity) for entity in self.migration_path
        }

    def run_migration(self):
        """Khởi chạy một phiên migrate mới."""

        # 1. Khởi tạo Dữ liệu/Service cho phiên chạy mới
        entity_id_maps = {
            'category': {},
            'product': {},
        }  # Bảng ánh xạ ID mới, trống cho mỗi phiên chạy

        for entity in self.migration_path:
            self.run_entity_migration(entity, entity_id_maps)



    def run_entity_migration(self, entity, entity_id_maps):
    # def run_entity_migration(self, entity_source_data, entity, entity_id_maps):
        entity_source_data = self.read_connector.get_all_entities(entity)
        mapper = self.entity_mappers.get(entity)
        for record in entity_source_data:
            # 2. Bước Validate
            is_valid, processed_record = mapper.validate_record(record)

            if is_valid:
                # 3. Bước Ánh xạ (sử dụng current_id_map của phiên chạy)
                target_data = mapper.to_target(
                    processed_record,
                    global_context={'entity_id_maps': entity_id_maps}
                )
                print('target_data: ', json.dumps(target_data, indent=4))
                # 4. Bước Ghi vào đích (WooCommerce)
                created_target_data = self.write_connector.create_entity(entity, target_data)

                mapper.post_process(
                    global_context={
                        'entity_id_maps': entity_id_maps,
                        'source_data': record,
                        'created_target_data': created_target_data,
                        'write_connector': self.write_connector,
                    }
                )
