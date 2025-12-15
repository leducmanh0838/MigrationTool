# --- MigrationService.py (Quản lý phiên chạy) ---
import json

from config.settings import MagentoConfig, WordPressConfig
from src.connectors.read_connectors.magento_connector import MagentoConnector
from src.connectors.read_connectors.read_base_connector import ReadBaseConnector
from src.connectors.write_connectors.woocommerce_connector import WooCommerceConnector
from src.connectors.write_connectors.write_base_connector import WriteBaseConnector
from src.mappers.entity_migration_mapper import EntityMigrationMapper


class MigrationService:
    def __init__(self, migration_path: list, write_connector: WriteBaseConnector, read_connector: ReadBaseConnector):
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
        migration_context = {
            "entity_id_maps": {
                'category': {},
                'product': {},
            }
        }

        for entity in self.migration_path:
            self._run_entity_migration(entity, migration_context)

            print("migration_context: ", json.dumps(migration_context, indent=4))

    def _run_entity_migration(self, entity, migration_context):
        entity_source_data = self.read_connector.get_all_entities(entity)
        mapper = self.entity_mappers.get(entity)
        for record in entity_source_data:
            # 2. Bước Validate
            is_valid, validated_record = mapper.validate_record(record)

            if is_valid:
                # 3. Bước Ánh xạ (sử dụng current_id_map của phiên chạy)
                target_data = mapper.to_record_target(
                    validated_record,
                    context=migration_context
                )
                print('target_data: ', json.dumps(target_data, indent=4))
                # 4. Bước Ghi vào đích (WooCommerce)
                created_target_record = self.write_connector.create_entity(entity, target_data)

                mapper.post_process(source_record=validated_record, created_target_record=created_target_record,
                                    context=migration_context)


if __name__ == "__main__":
    magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)
    woo_connector = WooCommerceConnector(WordPressConfig.BASE_URL, WordPressConfig.USERNAME,
                                         WordPressConfig.PASSWORD)
    service = MigrationService(
        # schema_mapper=schema_manager,
        migration_path=['category', 'product', 'customer'],
        # migration_path=['product'],
        read_connector=magento_connector,
        write_connector=woo_connector,
    )

    service.run_migration()
