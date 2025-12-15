# /src/utils/common_transformers.py
import json

from config.settings import YamlValueConfig


def test_transformation(value1, value2):
    return {
        value1: value1,
        value2: value2,
    }


def map_id_to_target(entity, source_id, context):
    print("map_id_to_target:")
    if context and context.get('entity_id_maps') and context.get('entity_id_maps').get(entity):
        category_id_map = context.get('entity_id_maps').get(entity)
        return category_id_map.get(source_id)
    return 0


def map_ids_to_target(entity, source_ids: list, context):
    print(f"map_ids_to_target")
    print(f"entity ", entity)
    print(f"source_ids ", json.dumps(source_ids, indent=4))
    print(f"context ", json.dumps(context, indent=4))

    if (context and
            context.get('entity_id_maps') and
            context['entity_id_maps'].get(entity)):

        category_id_map = context['entity_id_maps'][entity]

        # Sử dụng list comprehension để ánh xạ từng ID nguồn
        target_ids = []
        for source_id in source_ids:
            target_id = category_id_map.get(int(source_id.get("id")))
            if target_id is not None and target_id != 0:
                target_ids.append({"id": target_id})
        print(f"target_ids ", json.dumps(target_ids, indent=4))
        return target_ids
    return []


def normalize_string_mapper(value: str, **kwargs) -> str:
    """Chuẩn hóa chuỗi (loại bỏ khoảng trắng thừa, xử lý None)."""
    print('normalize_string_mapper')
    if value is None:
        return ""
    return str(value).strip()


def html_cleanup_mapper(html_content: str, **kwargs) -> str:
    """Hàm làm sạch HTML, áp dụng cho description của nhiều entity."""
    print('html_cleanup_mapper')
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
    print("transform_magento_value")
    print("params: ", value, source_platform, target_platform, entity, field, default_value)
    try:
        return YamlValueConfig.YAML_TRANSFORMATION_CONFIGS.get(source_platform).get(entity).get(field).get(value).get(
            target_platform)
    except Exception:
        return default_value
