# /src/utils/common_transformers.py


def map_id_to_target(value, entity, source_id_field, **kwargs):
    print("map_id_to_target:")
    print("value: ", value)
    print("entity: ", entity)
    print("source_id_field: ", source_id_field)
    print("kwargs: ", kwargs)
    if kwargs and kwargs.get('entity_id_maps') and kwargs.get('entity_id_maps').get(entity):
        print("kwargs and kwargs.get('entity_id_maps') and kwargs.get('entity_id_maps').get(entity): = True")
        category_id_map = kwargs.get('entity_id_maps').get(entity)
        return category_id_map.get(value)
    print("value=0")
    return 0


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


def transform_magento_value(magento_value: int,
                            target_platform: str,
                            default_value: str,
                            data_mapping=None,
                            **kwargs) -> str:
    print("transform_magento_status")
    platform_mappings = data_mapping.get(magento_value)

    if platform_mappings is None:
        return default_value

    target_value = platform_mappings.get(target_platform)

    if target_value is None:
        return default_value

    return target_value