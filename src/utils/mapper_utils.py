import json
import typing

import jmespath

from config.settings import YamlValueConfig


def get_func_by_func_config(func_config, func_name_list: dict):
    return func_name_list.get(func_config.get("function_name"))


def resolve_dynamic_params(
        func_config=None,
        source_value=None,
        source_record=None,
        created_target_record=None,
        context=None
):
    """Phân giải các tham số động ($QUERY, $SOURCE_VALUE, $CONTEXT_MAPPER)."""
    resolved_params = {}
    static_params = func_config.get('params', {})

    for key, val in static_params.items():
        if isinstance(val, str) and val.startswith('$'):
            if val == '$SOURCE_VALUE':
                resolved_params[key] = source_value
            elif val == '$SOURCE_RECORD':
                resolved_params[key] = source_record
            elif val == '$YAML_TRANSFORMATION_CONFIGS':
                resolved_params[key] = YamlValueConfig.YAML_TRANSFORMATION_CONFIGS
            elif val == '$CREATED_TARGET_RECORD':
                resolved_params[key] = created_target_record
            elif val == '$CONTEXT':
                resolved_params[key] = context
            elif val.startswith('$QUERY.'):
                # Thực thi JMESPath Query trên toàn bộ bản ghi nguồn
                jmes_query = val.split('.', 1)[1]
                resolved_params[key] = jmespath.search(jmes_query, source_record)
            # Không xử lý $SOURCE_RECORD và $CONFIG trong ví dụ này
        else:
            resolved_params[key] = val

    return resolved_params


def unflatten_json(flat_data):
    """
  Chuyển đổi dữ liệu JSON phẳng (sử dụng dấu chấm cho phân cấp)
  thành dữ liệu JSON lồng nhau (nested JSON) phù hợp để gửi API WooCommerce.
  """
    nested_data = {}

    for key, value in flat_data.items():
        # Tách khóa bằng dấu chấm ('.') để xác định các cấp
        parts = key.split('.')

        # Bắt đầu từ cấp gốc (root)
        current_dict = nested_data

        # Duyệt qua các phần của khóa, trừ phần cuối cùng
        for part in parts[:-1]:
            # Nếu khóa cấp này chưa tồn tại, tạo một dictionary mới
            if part not in current_dict:
                current_dict[part] = {}
            elif isinstance(current_dict[part], list):
                break
            # Di chuyển xuống cấp tiếp theo
            current_dict = current_dict[part]

        # Gán giá trị cho khóa cuối cùng
        last_part = parts[-1]
        current_dict[last_part] = value

    return nested_data


if __name__ == "__main__":
    x = {
        "status": "processing",
        "date_created": "2025-11-26 18:22:21",
        "order_key": "000000001",
        "payment_method": "checkmo",
        "billing.first_name": "Veronica",
        "billing.last_name": "Costello",
        "billing.address_1": "6146 Honey Bluff Parkway",
        "billing.city": "Calder",
        "billing.state": "Michigan",
        "billing.postcode": "49628-7978",
        "billing.country": "US",
        "billing.email": "roni_cost@example.com",
        "billing.phone": "(555) 229-3326",
        "shipping.first_name": "Veronica",
        "shipping.last_name": "Costello",
        "shipping.address_1": "6146 Honey Bluff Parkway",
        "shipping.city": "Calder",
        "shipping.state": "Michigan",
        "shipping.postcode": "49628-7978",
        "shipping.country": "US",
        "shipping.phone": "(555) 229-3326",
        "line_items": [
            {
                "amount_refunded": 0,
                "base_amount_refunded": 0,
                "base_discount_amount": 0,
                "base_discount_invoiced": 0,
                "base_discount_tax_compensation_amount": 0,
                "base_discount_tax_compensation_invoiced": 0,
                "base_original_price": 29,
                "base_price": 29,
                "base_price_incl_tax": 31.39,
                "base_row_invoiced": 29,
                "base_row_total": 29,
                "base_row_total_incl_tax": 31.39,
                "base_tax_amount": 2.39,
                "base_tax_invoiced": 2.39,
                "created_at": "2025-11-26 18:22:21",
                "discount_amount": 0,
                "discount_invoiced": 0,
                "discount_percent": 0,
                "free_shipping": 0,
                "discount_tax_compensation_amount": 0,
                "discount_tax_compensation_invoiced": 0,
                "is_qty_decimal": 0,
                "item_id": 1,
                "name": "Iris Workout Top",
                "no_discount": 0,
                "order_id": 1,
                "original_price": 29,
                "price": 29,
                "price_incl_tax": 31.39,
                "product_id": 1428,
                "product_type": "configurable",
                "qty_canceled": 0,
                "qty_invoiced": 1,
                "qty_ordered": 1,
                "qty_refunded": 0,
                "qty_shipped": 1,
                "row_invoiced": 29,
                "row_total": 29,
                "row_total_incl_tax": 31.39,
                "row_weight": 1,
                "sku": "WS03-XS-Red",
                "store_id": 1,
                "tax_amount": 2.39,
                "tax_invoiced": 2.39,
                "tax_percent": 8.25,
                "updated_at": "2025-11-26 18:22:21",
                "weight": 1,
                "product_option": {
                    "extension_attributes": {
                        "configurable_item_options": [
                            {
                                "option_id": "144",
                                "option_value": 166
                            },
                            {
                                "option_id": "93",
                                "option_value": 58
                            }
                        ]
                    }
                },
                "extension_attributes": {
                    "itemized_taxes": []
                }
            }
        ],
        "line_items.total_tax": 2.39,
        "total": 36.39,
        "shipping_total": 5,
        "shipping_tax": 0,
        "discount_total": 0
    }

    print(json.dumps(unflatten_json(x), indent=4))
