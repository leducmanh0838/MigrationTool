from src.connectors.read_connectors.magento_connector import MagentoConnector
from src.connectors.write_connectors.woocommerce_connector import WooCommerceConnector
from src.utils import validators, transformers, processors

POST_PROCESSOR_FUNCTIONS = {
    'save_id_mapping': processors.save_id_mapping,
    'send_reset_password_email': processors.send_reset_password_email,
}

TRANSFORMER_FUNCTIONS = {
    'test_transformation': transformers.test_transformation,
    'normalize_string_mapper': transformers.normalize_string_mapper,
    'html_cleanup_mapper': transformers.html_cleanup_mapper,
    'price_rounding_mapper': transformers.price_rounding_mapper,
    'map_id_to_target': transformers.map_id_to_target,
    'map_ids_to_target': transformers.map_ids_to_target,
    'transform_magento_value': transformers.transform_magento_value,
    'null_to_empty_string': transformers.null_to_empty_string,
    'order_line_item_format_totals_to_string': transformers.order_line_item_format_totals_to_string,
}

VALIDATOR_FUNCTIONS = {
    'not_null': validators.not_null,
    'is_not_self_referencing': validators.is_not_self_referencing,
    'is_string_min_length': validators.is_string_min_length,
    'is_string_max_length': validators.is_string_max_length,
    'is_integer': validators.is_integer,
    'is_non_negative_integer': validators.is_non_negative_integer,
    'is_max_value': validators.is_max_value,
    'is_valid_email': validators.is_valid_email,
}

CONNECTOR_CLASSES = {
    'MagentoConnector': MagentoConnector,
    'WooCommerceConnector': WooCommerceConnector,
}
