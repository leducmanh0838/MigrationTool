from src.utils.post_processor_utils import common_processors
from src.utils.transformation_utils import common_transformers
from src.utils.validator_utils import common_validators

POST_PROCESSOR_FUNCTIONS = {
    'save_id_mapping': common_processors.save_id_mapping,
    'send_reset_password_email': common_processors.send_reset_password_email,
}

TRANSFORMER_FUNCTIONS = {
    'test_transformation': common_transformers.test_transformation,
    'normalize_string_mapper': common_transformers.normalize_string_mapper,
    'html_cleanup_mapper': common_transformers.html_cleanup_mapper,
    'price_rounding_mapper': common_transformers.price_rounding_mapper,
    'map_id_to_target': common_transformers.map_id_to_target,
    'map_ids_to_target': common_transformers.map_ids_to_target,
    'transform_magento_value': common_transformers.transform_magento_value,
}

VALIDATOR_FUNCTIONS = {
    'not_null': common_validators.not_null,
    'is_not_self_referencing': common_validators.is_not_self_referencing,
    'is_string_min_length': common_validators.is_string_min_length,
    'is_string_max_length': common_validators.is_string_max_length,
    'is_integer': common_validators.is_integer,
    'is_non_negative_integer': common_validators.is_non_negative_integer,
    'is_max_value': common_validators.is_max_value,
    'is_valid_email': common_validators.is_valid_email,
}