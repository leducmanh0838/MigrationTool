from typing import Dict, Any

from config.yaml_configs import VALIDATOR_FUNCTIONS
from src.utils import mapper_utils


class EntityMigrationMapper:
    def __init__(self, source: str, target: str, entity: str):
        self.source = source
        self.target = target
        self.entity = entity

        self.mapping_config = mapper_utils.get_mapping_config(source, target, entity)
        self.field_mappings = self.mapping_config.get('fields', {})
        self.transformations_config = self.mapping_config.get('transformations', {})
        self.special_transformations_config = self.mapping_config.get('special_transformations', {})
        self.validators_config = self.mapping_config.get('validators', {})
        self.post_processors_config = self.mapping_config.get('post_processors', {})
        # ID Map: {Magento_ID: Woo_ID}
        # self.id_map = {}

    # def add_id_map(self, magento_id, woo_id):
    #     self.id_map[magento_id] = woo_id

    def to_target(self, source_data: Dict[str, Any], global_context) -> Dict[str, Any]:
        """Thực hiện ánh xạ động Category."""
        target_data: Dict[str, Any] = {}

        # Ánh xạ các trường từ YAML
        for source_field, target_field in self.field_mappings.items():
            value = source_data.get(source_field)
            field_transformations = self.transformations_config.get(source_field)
            if field_transformations:
                value = mapper_utils.apply_transformations(value, field_transformations, global_context)
            target_data[target_field] = value

        mapper_utils.transform_special_field(source_data, target_data, self.special_transformations_config)
        return target_data

    def validate_record(self, source_record):
        """
        Thực hiện xác thực trên một bản ghi dữ liệu nguồn (Magento).

        :param source_record: Dict chứa dữ liệu bản ghi, ví dụ: {'parent_id': '10', 'name': 'Áo', 'position': '1'}
        :return: (Boolean, dict) - (Có hợp lệ không, Bản ghi đã được điều chỉnh/xử lý)
        """
        processed_record = source_record.copy()

        for source_field, rules in self.validators_config.items():
            value = processed_record.get(source_field)

            for rule in rules:
                function_name = rule['function_name']
                on_fail = rule.get('on_fail')
                params = rule.get('params', {})
                default_value = rule.get('default_value')  # Chỉ dùng cho set_to_default

                # 1. Lấy hàm Python tương ứng
                validator_func = VALIDATOR_FUNCTIONS.get(function_name)
                if not validator_func:
                    print(f"Lỗi: Không tìm thấy hàm xác thực '{function_name}'")
                    continue

                # 2. Thực thi hàm xác thực
                # is_valid, error_message = validator_func(value, **params)
                is_valid = validator_func(value, **params)

                # 3. Xử lý khi xác thực THẤT BẠI
                if not is_valid:
                    print(
                        f"Xác thực thất bại cho trường '{source_field}' với quy tắc '{function_name}'. Lỗi")

                    if on_fail == 'skip_record':
                        # Bỏ qua toàn bộ bản ghi này
                        print("Hành động: Bỏ qua bản ghi.")
                        return False, processed_record

                    elif on_fail == 'log_warning':
                        # Chỉ ghi log cảnh báo và tiếp tục
                        print("Hành động: Ghi cảnh báo và tiếp tục.")
                        continue  # Chuyển sang quy tắc tiếp theo hoặc trường tiếp theo

                    elif on_fail == 'set_to_default':
                        # Đặt lại giá trị của trường về giá trị mặc định
                        print(f"Hành động: Đặt giá trị mặc định '{default_value}'.")
                        processed_record[source_field] = default_value
                        value = default_value  # Cập nhật giá trị để các quy tắc sau sử dụng giá trị mới
                        # Vẫn cần kiểm tra lại (Tùy logic: một số người sẽ dừng và coi giá trị mới là hợp lệ,
                        # một số sẽ tiếp tục chạy các quy tắc khác trên giá trị mặc định)

                    elif on_fail == 'truncate_value':
                        # Cắt bớt giá trị (dùng cho is_max_value)
                        max_value = params.get('max_value')
                        if max_value is not None:
                            print(f"Hành động: Cắt bớt giá trị về {max_value}.")
                            processed_record[source_field] = max_value
                            value = max_value
                        else:
                            print("Lỗi: 'truncate_value' được gọi nhưng không có 'max_value'.")

                    # ... có thể thêm các hành động on_fail khác (ví dụ: raise_exception)

        # 4. Nếu vượt qua tất cả các xác thực (hoặc đã được xử lý), trả về True
        return True, processed_record

    def post_process(self, global_context):
        mapper_utils.post_process_util(self.post_processors_config, global_context=global_context)
