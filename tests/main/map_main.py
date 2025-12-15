# /src/main.py
import json

from config.settings import WooCommerceConfig, MagentoConfig, WordPressConfig
from src.connectors.read_connectors.magento_connector import MagentoConnector
from src.connectors.write_connectors.woocommerce_connector import WooCommerceConnector
from src.services.migration_service import MigrationService

# --- Dữ liệu Magento Category Nguồn ---
# Tôi sẽ định nghĩa dữ liệu này ở đây để tiện chạy thử
MAGENTO_SOURCE_DATA = [
    {"id": 2, "parent_id": 0, "name": "Default Category", "is_active": True, "level": 1, "product_count": 272},
    {"id": 38, "parent_id": 2, "name": "Dhat's New", "is_active": True, "level": 2, "product_count": 0},
    # {"id": 20, "parent_id": 2, "name": "Women", "is_active": True, "level": 2, "product_count": 0},
    # {"id": 21, "parent_id": 20, "name": "Tops", "is_active": True, "level": 3, "product_count": 50},
    # {"id": 23, "parent_id": 21, "name": "Jackets", "is_active": True, "level": 4, "product_count": 12},
    # {"id": 24, "parent_id": 21, "name": "Hoodies & Sweatshirts", "is_active": True, "level": 4, "product_count": 12},
    # {"id": 26, "parent_id": 21, "name": "Bras & Tanks", "is_active": True, "level": 4, "product_count": 14},
    # {"id": 22, "parent_id": 20, "name": "Bottoms", "is_active": True, "level": 3, "product_count": 25},
    # {"id": 11, "parent_id": 2, "name": "Men", "is_active": True, "level": 2, "product_count": 0},
    # # Thêm một category Tiếng Việt để test slug
    # {"id": 100, "parent_id": 11, "name": "Thời Trang Nam Mới", "is_active": True, "level": 3, "product_count": 5}
]


def run_category_migration():
    print("--- BẮT ĐẦU MIGRATION CATEGORY ---")
    # 1. Khởi tạo Schema Mapper
    try:
        # 2. Khởi tạo Category Mapper
        magento_connector = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)
        woo_connector = WooCommerceConnector(WooCommerceConfig.BASE_URL, WordPressConfig.USERNAME,
                                             WordPressConfig.PASSWORD)
        category_migration_service = MigrationService(
            # schema_mapper=schema_manager,
            # migration_path=['category', 'product'],
            migration_path=['customer'],
            read_connector=magento_connector,
            write_connector=woo_connector,
        )

    except ValueError as e:
        print(f"❌ Lỗi khởi tạo Mapper: {e}")
        return

    # print("category_mapper.mapping_config")
    # print(json.dumps(category_mapper.mapping_config, indent=4))

    # magento_data = magento_connector.get_all_categories()
    category_migration_service.run_migration()
    # 3. Lặp qua dữ liệu nguồn và thực hiện ánh xạ

    # id_map = {}
    # target_categories = []
    # for source_category in MAGENTO_SOURCE_DATA:
    #     print("*" * 20)
    #     target_cat = category_migration_service.to_target(source_category, id_map)
    #     target_categories.append(target_cat)
    #     # is_valid, validated_source_category = category_mapper.validate_record(source_category)
    #     # print("is_valid: ", is_valid)
    #     # if is_valid:
    #     #     target_cat = category_mapper.to_target(validated_source_category, id_map)
    #     #     created_target_category = woo_connector.create_category(target_cat)
    #     #     id_map[validated_source_category["id"]] = created_target_category["id"]
    #     # category_mapper.add_id_map(source_category["id"], created_target_category["id"])
    #
    # print("\n--- KẾT QUẢ CHUYỂN ĐỔI CATEGORY (WooCommerce Format) ---")
    #
    # # In kết quả dưới dạng JSON đẹp mắt
    # print(json.dumps(target_categories, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    # Lưu ý: Bạn cần phải chạy file này từ thư mục gốc của dự án
    # hoặc thêm thư mục gốc vào PYTHONPATH để import config.settings và src.core

    # Giả sử bạn đã cài đặt 'PyYAML' và 'unidecode'
    run_category_migration()
