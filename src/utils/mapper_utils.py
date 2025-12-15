import yaml

from config.settings import AppConfig
from config.yaml_configs import TRANSFORMER_FUNCTIONS, MAGENTO_DATA_MAPPINGS, POST_PROCESSOR_FUNCTIONS, \
    SPECIAL_TRANSFORMER_FUNCTIONS


def get_mapping_config(source: str, target: str, entity: str):
    filename = f"{entity}_{source}_{target}.yaml"
    filepath = f"{AppConfig.YAML_MAPPINGS_DIR}/{filename}"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            mapping_data = yaml.safe_load(f)
            # key = f"{source}-{target}-{entity}"
            # self._mappings[key] = mapping_data
            # print(f"✅ Đã tải ánh xạ: {key}")
            return mapping_data
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file ánh xạ tại {filepath}")
        return False
    except yaml.YAMLError as e:
        print(f"❌ Lỗi khi phân tích file YAML {filepath}: {e}")
        return False


def get_transformation_function(transformations, field_name: str):
    """
    Tìm và trả về hàm chuyển đổi (Python function) dựa trên định nghĩa YAML.
    """

    if field_name in transformations:
        transform_def = transformations[field_name]
        # print(json.dumps(transform_def, indent=4))

        if transform_def.get('type') == 'function':
            function_name = transform_def['function_name']

            try:
                # Lấy đối tượng hàm từ module đã tải bằng tên chuỗi
                func = TRANSFORMER_FUNCTIONS.get(function_name)
                if callable(func):
                    return func
                else:
                    print(f"Lỗi: '{function_name}' không phải là một hàm.")
                    return None
            except AttributeError:
                print(f"Lỗi: Không tìm thấy hàm '{function_name}' trong module mapper.")
                return None

    return None


def apply_transformations(source_value, field_transformations_config, global_context=None):
    """
    Áp dụng một loạt các phép biến đổi lên một giá trị nguồn.

    :param global_context: Các dữ liệu toàn cục cần thiết (như entity_id_maps, kết nối DB).
    :param field_transformations_config: Danh sách cấu hình transformation từ YAML.
    :param source_value: Giá trị dữ liệu ban đầu (từ Magento).
    :return: Giá trị sau khi đã được biến đổi.
    """
    MAPPING_REF_KEY = '_mapping_ref'
    if global_context is None:
        global_context = {}

    current_value = source_value
    for transformation in field_transformations_config:
        try:
            # Lấy tên hàm từ cấu hình
            if transformation.get('type') != "function":
                continue
            function_name = transformation.get('function_name')
            # Lấy các tham số cụ thể từ YAML (nếu có), xử lý _mapping_ref
            yaml_params = transformation.get('params', {})
            if MAPPING_REF_KEY in yaml_params:
                mapping_key = yaml_params.pop(MAPPING_REF_KEY)
                data_mapping = MAGENTO_DATA_MAPPINGS.get(mapping_key)
                yaml_params['data_mapping'] = data_mapping

            # Lấy hàm thực tế từ registry
            transform_func = TRANSFORMER_FUNCTIONS.get(function_name)

            if not transform_func:
                print(f"Lỗi: Hàm transformation '{function_name}' không được tìm thấy trong registry.")
                continue

            # Kết hợp các tham số từ YAML và Context thành kwargs
            kwargs = {**yaml_params, **global_context}
            # kwargs = {**yaml_params}

            # Gọi hàm transformation
            # Lưu ý: Hàm phải được định nghĩa để nhận (value, **kwargs)
            current_value = transform_func(current_value, **kwargs)

        except Exception as e:
            print(f"Lỗi khi thực thi transformation cho giá trị '{source_value}': {e}")

    return current_value


def transform_special_field(source_value, target_data, special_transformations_config):
    for special_transformation in special_transformations_config:
        try:
            # Lấy tên hàm từ cấu hình
            if special_transformation.get('type') != "function":
                continue
            function_name = special_transformation.get('function_name')
            # Lấy các tham số cụ thể từ YAML (nếu có), xử lý _mapping_ref
            yaml_params = special_transformation.get('params', {})

            # Lấy hàm thực tế từ registry
            special_transform_func = SPECIAL_TRANSFORMER_FUNCTIONS.get(function_name)

            if not special_transform_func:
                print(f"Lỗi: Hàm transformation '{function_name}' không được tìm thấy trong registry.")
                continue

            # Kết hợp các tham số từ YAML và Context thành kwargs
            kwargs = {**yaml_params}
            # kwargs = {**yaml_params}

            # Gọi hàm transformation
            # Lưu ý: Hàm phải được định nghĩa để nhận (value, **kwargs)
            special_transform_func(source_value, target_data, **kwargs)

        except Exception as e:
            print(f"Lỗi khi thực thi special transformation cho giá trị '{source_value}': {e}")


def post_process_util(post_processors, global_context=None):
    if global_context is None:
        global_context = {}
    for post_processor in post_processors:
        try:
            if post_processor.get('type') != "function":
                continue
            function_name = post_processor.get('function_name')
            yaml_params = post_processor.get('params', {})

            transform_func = POST_PROCESSOR_FUNCTIONS.get(function_name)

            if not transform_func:
                print(f"Lỗi: Hàm post processor '{function_name}' không được tìm thấy trong registry.")
                continue

            kwargs = {**yaml_params, **global_context}
            transform_func(**kwargs)

        except Exception as e:
            print(f"Lỗi khi thực thi post_process_util: {e}")

# if __name__ == '__main__':
#     mapping_config = get_mapping_config(source="magento", target="woo", entity="category")
#     print(json.dumps(mapping_config.get("transformations"), indent=4))
#     func = get_transformation_function(mapping_config.get("validators"), "name")
#     print(func(" AB C   "))
