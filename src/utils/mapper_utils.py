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
