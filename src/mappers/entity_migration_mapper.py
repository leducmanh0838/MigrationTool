import json
from typing import Dict, Any

import jmespath

from config.settings import YamlValueConfig
from src.utils.yaml_lookup import VALIDATOR_FUNCTIONS, TRANSFORMER_FUNCTIONS, POST_PROCESSOR_FUNCTIONS
from src.utils import mapper_utils


class EntityMigrationMapper:
    def __init__(self, source: str, target: str, entity: str, field_parts=None):
        mapping_config = YamlValueConfig.YAML_MAPPINGS.get(source).get(target).get(entity)
        self.primary_source = mapping_config.get("keys", {}).get("primary_source", "id")
        self.primary_target = mapping_config.get("keys", {}).get("primary_target", "id")
        self.field_mappings = mapping_config.get('fields', {})
        self.transformations_config = mapping_config.get('transformations', {})
        # self.special_transformations_config = mapping_config.get('special_transformations', {})
        self.validators_config = mapping_config.get('validators', {})
        self.post_processors_config = mapping_config.get('post_processors', {})

    def to_record_target(self, source_record: Dict[str, Any], context=None) -> Dict[str, Any]:
        target_data: Dict[str, Any] = {}

        for target_field, jmes_query in self.field_mappings.items():
            value = jmespath.search(jmes_query, source_record)
            if value is None:
                continue
            func_configs = self.transformations_config.get(target_field, {})
            for func_config in func_configs:
                params = mapper_utils.resolve_dynamic_params(func_config=func_config, source_value=value,
                                                             source_record=source_record,
                                                             context=context)
                func = mapper_utils.get_func_by_func_config(func_config, TRANSFORMER_FUNCTIONS)
                value = func(**params)

            target_data[target_field] = value
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
                    if on_fail == 'skip_record':
                        return False, source_record

                    elif on_fail == 'log_warning':
                        continue

                    elif on_fail == 'set_to_default':
                        source_record[source_field] = default_value

                    elif on_fail == 'truncate_value':
                        max_value = params.get('max_value')
                        if max_value is not None:
                            source_record[source_field] = max_value
        return True, source_record

if __name__ == '__main__':
    mapper = EntityMigrationMapper("magento", "woo", "category")
    print(mapper.primary_source)
    print(mapper.primary_target)