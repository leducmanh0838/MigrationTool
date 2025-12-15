# main.py

import yaml
import jmespath
import json
import os

# Import tất cả các hàm và lớp từ common_utils
from common_utils import MockMappingManager, map_id_to_target, not_null, is_not_self_referencing

# --- 1. Cấu hình các đối tượng Context (State) và Hàm ---
CONTEXT_MAPPER = MockMappingManager()
TRANSFORM_FUNCTIONS = {'map_id_to_target': map_id_to_target}
VALIDATOR_FUNCTIONS = {
    'not_null': not_null,
    'is_not_self_referencing': is_not_self_referencing
}


def load_yaml_config(file_path):
    """Tải và trả về nội dung file YAML."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def resolve_dynamic_params(func_config, source_value, source_record):
    """Phân giải các tham số động ($QUERY, $SOURCE_VALUE, $CONTEXT_MAPPER)."""
    resolved_params = {}
    static_params = func_config.get('params', {})

    for key, val in static_params.items():
        if isinstance(val, str) and val.startswith('$'):
            if val == '$SOURCE_VALUE':
                resolved_params[key] = source_value
            elif val == '$CONTEXT_MAPPER':
                resolved_params[key] = CONTEXT_MAPPER
            elif val.startswith('$QUERY.'):
                # Thực thi JMESPath Query trên toàn bộ bản ghi nguồn
                jmes_query = val.split('.', 1)[1]
                resolved_params[key] = jmespath.search(jmes_query, source_record)
            # Không xử lý $SOURCE_RECORD và $CONFIG trong ví dụ này
        else:
            resolved_params[key] = val

    return resolved_params


def apply_transformations(field_name, value, config, source_record):
    """Áp dụng tất cả các hàm transformation cho một trường."""
    if field_name not in config.get('transformations', {}):
        return value

    current_value = value
    for t_rule in config['transformations'][field_name]:
        func_name = t_rule['function_name']
        func = TRANSFORM_FUNCTIONS[func_name]

        # 1. Phân giải tham số động
        resolved_params = resolve_dynamic_params(t_rule, current_value, source_record)

        # 2. Gọi hàm Transform (Truyền giá trị vào vị trí 1, tham số động qua **kwargs)
        current_value = func(current_value, **resolved_params)

    return current_value


def apply_validators(field_name, value, config, source_record):
    """Áp dụng tất cả các hàm validator cho một trường."""
    if field_name not in config.get('validators', {}):
        return ('valid', value)

    for v_rule in config['validators'][field_name]:
        func_name = v_rule['function_name']
        func = VALIDATOR_FUNCTIONS[func_name]

        # 1. Phân giải tham số động
        resolved_params = resolve_dynamic_params(v_rule, value, source_record)

        # 2. Gọi hàm Validate (Truyền giá trị vào vị trí 1, tham số động qua **kwargs)
        is_valid = func(value, **resolved_params)

        if not is_valid:
            on_fail = v_rule.get('on_fail', 'log_warning')

            if on_fail == 'skip_record':
                print(f"[FAIL] VALIDATOR '{func_name}': Skip record due to invalid field '{field_name}'")
                return ('skip', value)
            elif on_fail == 'set_to_default':
                default_val = v_rule.get('default_value')
                print(f"[FAIL] VALIDATOR '{func_name}': Setting '{field_name}' to default: {default_val}")
                return ('valid', default_val)

    return ('valid', value)


def migrate_category(magento_record, config):
    """Thực hiện quá trình ánh xạ ETL cho một bản ghi."""
    woo_record = {}

    # --- BƯỚC 1: TRÍCH XUẤT DỮ LIỆU BẰNG JMESPATH ---
    extracted_data = {}
    for woo_field, jmes_query in config['fields'].items():
        # Thực thi JMESPath Query
        extracted_data[woo_field] = jmespath.search(jmes_query, magento_record)
    print("\n" + "=" * 50 + "\n")
    print("Extracted_data:\n", json.dumps(extracted_data, indent=4))

    # --- BƯỚC 2: VALIDATE VÀ TRANSFORM ---

    # Lưu ý: Lặp qua extracted_data để đảm bảo xử lý theo thứ tự của fields
    print("\n" + "=" * 50 + "\n")
    print("Validate:\n")
    for woo_field, extracted_value in extracted_data.items():

        # A. VALIDATE (Kiểm tra hợp lệ)
        status, validated_value = apply_validators(woo_field, extracted_value, config, magento_record)

        if status == 'skip':
            return None  # Bỏ qua bản ghi này

    #     # B. TRANSFORM (Biến đổi)
    #     final_value = apply_transformations(woo_field, validated_value, config, magento_record)
    #
    #     # Thêm vào bản ghi đích
    #     woo_record[woo_field] = final_value

    return woo_record


# --- DỮ LIỆU TEST ---
magento_test_data = {
    "id": 2,
    "parent_id": 0,
    "name": "Men's Clothing",
    "position": 1,
    "custom_attributes": [{"attribute_code": "children_count", "value": "10"}],
}

# Dữ liệu test gây lỗi (self-reference)
magento_self_ref_data = {
    "id": 3,
    "parent_id": 3,  # Lỗi: trỏ về chính nó
    "name": "Self-Referenced Cat",
    "position": 5,
    "custom_attributes": [{"attribute_code": "children_count", "value": "0"}],
}

# --- CHẠY CHƯƠNG TRÌNH ---
if __name__ == '__main__':
    # Cần đảm bảo thư viện pyyaml và jmespath đã được cài đặt: pip install pyyaml jmespath

    mapping_config = load_yaml_config('config/category_mapping.yaml')

    print("--- 1. TEST CASE HỢP LỆ (ID: 2) ---")
    print("\n" + "=" * 50 + "\n")
    print("Magento Source:\n", json.dumps(magento_test_data, indent=4))
    woo_category_valid = migrate_category(magento_test_data, mapping_config)

    # print("--- 2. TEST CASE GÂY LỖI VALIDATION (ID: 3 - Tự trỏ) ---")
    # woo_category_fail = migrate_category(magento_self_ref_data, mapping_config)
    # print("Magento Source:\n", json.dumps(magento_self_ref_data, indent=4))
    # print("\nWooCommerce Target (Sau lỗi):\n", json.dumps(woo_category_fail, indent=4))
