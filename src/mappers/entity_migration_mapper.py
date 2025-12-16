import json
from typing import Dict, Any

import jmespath

from config.settings import YamlValueConfig
from config.yaml_configs import VALIDATOR_FUNCTIONS, TRANSFORMER_FUNCTIONS, POST_PROCESSOR_FUNCTIONS
from src.utils import mapper_utils


class EntityMigrationMapper:
    def __init__(self, source: str, target: str, entity: str, field_parts=None):
        # self.source = source
        # self.target = target
        # self.entity = entity
        mapping_config = YamlValueConfig.YAML_MAPPINGS.get(source).get(target).get(entity)
        if field_parts is None:
            mapping_config = mapping_config.get(entity)
        else:
            for field_part in field_parts:
                mapping_config = mapping_config.get(field_part)
        self.field_mappings = mapping_config.get('fields', {})
        self.transformations_config = mapping_config.get('transformations', {})
        # self.special_transformations_config = mapping_config.get('special_transformations', {})
        self.validators_config = mapping_config.get('validators', {})
        self.post_processors_config = mapping_config.get('post_processors', {})

    def to_record_target(self, source_record: Dict[str, Any], context=None) -> Dict[str, Any]:
        target_data: Dict[str, Any] = {}
        print('source_data: ', json.dumps(source_record, indent=4))

        for target_field, jmes_query in self.field_mappings.items():
            # print("target_field: ", target_field)
            # Thực thi JMESPath Query
            value = jmespath.search(jmes_query, source_record)
            if value is None:
                continue
            func_configs = self.transformations_config.get(target_field, {})
            for func_config in func_configs:
                params = mapper_utils.resolve_dynamic_params(func_config=func_config, source_value=value,
                                                             source_record=source_record,
                                                             context=context)
                func = mapper_utils.get_func_by_func_config(func_config, TRANSFORMER_FUNCTIONS)
                # print("params: ", params)
                value = func(**params)

            target_data[target_field] = value
        # print('target_data before unflatten_json: ', json.dumps(target_data, indent=4))
        # print('END target_data before unflatten_json: ')
        target_data = mapper_utils.unflatten_json(target_data)
        return target_data

    def validate_record(self, source_record, context=None):
        for source_field, func_configs in self.validators_config.items():
            source_value = source_record.get(source_field)
            for func_config in func_configs:
                params = mapper_utils.resolve_dynamic_params(func_config, source_value, source_record, context)
                on_fail = func_config.get('on_fail')
                default_value = func_config.get('default_value')
                func = mapper_utils.get_func_by_func_config(func_config, VALIDATOR_FUNCTIONS)
                is_valid = func(**params)
                if not is_valid:
                    print(
                        f"Xác thực thất bại cho trường '{source_field}' với quy tắc '{func_config.get('function_name')}'. Lỗi")

                    if on_fail == 'skip_record':
                        # Bỏ qua toàn bộ bản ghi này
                        print("Hành động: Bỏ qua bản ghi.")
                        return False, source_record

                    elif on_fail == 'log_warning':
                        # Chỉ ghi log cảnh báo và tiếp tục
                        print("Hành động: Ghi cảnh báo và tiếp tục.")
                        continue  # Chuyển sang quy tắc tiếp theo hoặc trường tiếp theo

                    elif on_fail == 'set_to_default':
                        # Đặt lại giá trị của trường về giá trị mặc định
                        print(f"Hành động: Đặt giá trị mặc định '{default_value}'.")
                        source_record[source_field] = default_value
                        value = default_value  # Cập nhật giá trị để các quy tắc sau sử dụng giá trị mới
                        # Vẫn cần kiểm tra lại (Tùy logic: một số người sẽ dừng và coi giá trị mới là hợp lệ,
                        # một số sẽ tiếp tục chạy các quy tắc khác trên giá trị mặc định)

                    elif on_fail == 'truncate_value':
                        # Cắt bớt giá trị (dùng cho is_max_value)
                        max_value = params.get('max_value')
                        if max_value is not None:
                            print(f"Hành động: Cắt bớt giá trị về {max_value}.")
                            source_record[source_field] = max_value
                            value = max_value
                        else:
                            print("Lỗi: 'truncate_value' được gọi nhưng không có 'max_value'.")
        return True, source_record

    def post_process(self, source_record=None, created_target_record=None, context=None):
        # mapper_utils.post_process_util(self.post_processors_config, global_context=global_context)
        for func_config in self.post_processors_config:
            params = mapper_utils.resolve_dynamic_params(func_config=func_config,
                                                         source_record=source_record,
                                                         created_target_record=created_target_record,
                                                         context=context)
            func = mapper_utils.get_func_by_func_config(func_config, POST_PROCESSOR_FUNCTIONS)
            func(**params)


if __name__ == "__main__":
    magento_test_data = {
        "id": 2,
        "parent_id": 0,
        "name": "Men's Clothing",
        "position": 1,
        "custom_attributes": [{"attribute_code": "children_count", "value": "10"}],
    }

    migration = EntityMigrationMapper("magento", "woo", "category", ["abc"])
    valid = migration.validate_record(magento_test_data, None)
    target_data = migration.to_record_target(magento_test_data, None)
    print('migration.field_mappings', json.dumps(migration.field_mappings, indent=4))
    print('migration.transformations_config', json.dumps(migration.transformations_config, indent=4))
