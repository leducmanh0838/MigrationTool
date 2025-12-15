import yaml

from config.settings import AppConfig
from src.utils.post_processor_utils import common_processors
from src.utils.transformation_utils import common_transformers
from src.utils.transformation_utils.special_transformation_utils.magento_woo_transformers.magento_woo_custom_address_transformers import \
    map_magento_addresses_to_woo_objects
from src.utils.validator_utils import common_validators

POST_PROCESSOR_FUNCTIONS = {
    'save_id_mapping': common_processors.save_id_mapping,
    'send_reset_password_email': common_processors.send_reset_password_email,
}

TRANSFORMER_FUNCTIONS = {
    'normalize_string_mapper': common_transformers.normalize_string_mapper,
    'html_cleanup_mapper': common_transformers.html_cleanup_mapper,
    'price_rounding_mapper': common_transformers.price_rounding_mapper,
    'map_id_to_target': common_transformers.map_id_to_target,
    'transform_magento_value': common_transformers.transform_magento_value,
}

SPECIAL_TRANSFORMER_FUNCTIONS = {
    'map_magento_addresses_to_woo_objects': map_magento_addresses_to_woo_objects,
}

VALIDATOR_FUNCTIONS = {
    'not_null': common_validators.not_null,
    'is_string_min_length': common_validators.is_string_min_length,
    'is_string_max_length': common_validators.is_string_max_length,
    'is_integer': common_validators.is_integer,
    'is_non_negative_integer': common_validators.is_non_negative_integer,
    'is_max_value': common_validators.is_max_value,
    'is_valid_email': common_validators.is_valid_email,
}

with open(AppConfig.YAML_CONFIG_DIR / "magento_data_mappings.yaml", 'r', encoding='utf-8') as f:
    MAGENTO_DATA_MAPPINGS = yaml.safe_load(f)