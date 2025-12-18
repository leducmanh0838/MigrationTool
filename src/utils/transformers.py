# /src/utils/transformers.py
import json

from config.settings import YamlValueConfig
from src.database.dao.id_mapping_dao import IdMappingDAO
from src.database.session import get_db


def test_transformation(value1, value2):
    return {
        value1: value1,
        value2: value2,
    }


def map_id_to_target(entity, source_id, default_value=0, context=None):
    with get_db() as db:
        dao = IdMappingDAO(db)
        record = dao.find_one_by(
            entity_name=entity,
            source_entity_id=source_id,
            migration_id=context.get("migration_id", 0)
        )
        if record:
            return record.target_entity_id
        return default_value


def map_ids_to_target(entity, source_ids: list, context):

    source_ids_dict = [item['id'] for item in source_ids]

    with get_db() as db:
        dao = IdMappingDAO(db)
        records = dao.filter_by(
            filters={
                "entity_name": entity,
                "source_entity_id": source_ids_dict,
                "migration_id": context.get("migration_id", 0)
            }
        )
        target_ids = [{"id": record.id} for record in records]
        return target_ids


def normalize_string_mapper(value: str, **kwargs) -> str:
    """Chuẩn hóa chuỗi (loại bỏ khoảng trắng thừa, xử lý None)."""
    if value is None:
        return ""
    return str(value).strip()


def html_cleanup_mapper(html_content: str, **kwargs) -> str:
    """Hàm làm sạch HTML, áp dụng cho description của nhiều entity."""
    # Logic làm sạch HTML chung...
    import re
    clean_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    return clean_content


def price_rounding_mapper(price: float | int, decimals: int = 2, **kwargs) -> float:
    """Hàm làm tròn giá, áp dụng cho price, regular_price, sale_price."""
    if price is None:
        return 0.0
    return round(price, decimals)


def transform_magento_value(value: int, source_platform: str,
                            target_platform: str, entity: str, field: str,
                            default_value: str) -> str:
    try:
        return YamlValueConfig.YAML_TRANSFORMATION_CONFIGS.get(source_platform).get(entity).get(field).get(value).get(
            target_platform)
    except Exception:
        return default_value


def null_to_empty_string(value) -> str:
    if value is None:
        return ""
    return value


def order_line_item_format_totals_to_string(source_value):
    # source_value là mảng line_items đã được ánh xạ bởi JMESPath
    if not isinstance(source_value, list):
        return source_value

    for item in source_value:
        # Chuyển đổi các trường số (float/int) thành chuỗi,
        # giữ lại 2 chữ số thập phân nếu cần

        if 'total' in item and item['total'] is not None:
            # Ví dụ: 150.0000 -> "150.00"
            item['total'] = "{:.2f}".format(float(item['total']))

        if 'subtotal' in item and item['subtotal'] is not None:
            item['subtotal'] = "{:.2f}".format(float(item['subtotal']))

        if 'price' in item and item['price'] is not None:
            item['price'] = "{:.2f}".format(float(item['price']))

    return source_value
