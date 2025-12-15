import json
import os

import yaml
from dotenv import load_dotenv
from pathlib import Path

from src.utils import setting_utils

# Tải các biến môi trường từ file .env (nếu có)
# Việc này nên được gọi một lần khi ứng dụng khởi động
load_dotenv()


# --- CẤU HÌNH CHUNG CỦA ỨNG DỤNG ---
class AppConfig:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()

    # DEBUG_MODE sẽ là True nếu ENVIRONMENT là 'development'
    DEBUG_MODE = ENVIRONMENT == "development"

    # VERIFY_SSL:
    # Nếu đang ở môi trường dev (hoặc test), thường cho phép bỏ qua xác minh SSL (False)
    # vì môi trường dev/test có thể dùng chứng chỉ tự ký (self-signed certs)
    # Nếu ở môi trường production, LUÔN LUÔN phải bật xác minh SSL (True)
    VERIFY_SSL = not DEBUG_MODE  # True nếu không phải DEBUG_MODE (tức là True khi PROD)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    YAML_MAPPINGS_DIR = PROJECT_ROOT / 'config' / 'yaml_mappings'
    YAML_TRANSFORMATION_CONFIGS_DIR = PROJECT_ROOT / 'config' / 'yaml_transformation_configs'
    # module_name = f"src.utils.data_transformers"
    DATA_TRANSFORMER_PATH = 'src.mappers.data_mappers.data_transformers'
    DATA_VALIDATORS_PATH = 'src.mappers.data_mappers.data_validators'


# --- CẤU HÌNH MAGENTO (SOURCE) ---
class MagentoConfig:
    # Lấy URL cơ sở và xóa dấu gạch chéo cuối để chuẩn hóa
    BASE_URL = os.getenv("MAGENTO_BASE_URL", "").rstrip('/')

    # Token xác thực quản trị (Admin Token)
    ACCESS_TOKEN = os.getenv("MAGENTO_ACCESS_TOKEN")


# --- CẤU HÌNH WOOCOMMERCE (TARGET) ---
class WooCommerceConfig:
    # Lấy URL cơ sở và xóa dấu gạch chéo cuối để chuẩn hóa
    BASE_URL = os.getenv("WOO_BASE_URL", "").rstrip('/')

    # Key và Secret để xác thực qua OAuth 1.0a
    CONSUMER_KEY = os.getenv("WOO_CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("WOO_CONSUMER_SECRET")


# --- CẤU HÌNH WOOCOMMERCE (TARGET) ---
class WordPressConfig:
    # Lấy URL cơ sở và xóa dấu gạch chéo cuối để chuẩn hóa
    BASE_URL = os.getenv("WORD_PRESS_BASE_URL", "").rstrip('/')

    # Key và Secret để xác thực qua OAuth 1.0a
    USERNAME = os.getenv("WORD_PRESS_USERNAME")
    PASSWORD = os.getenv("WORD_PRESS_PASSWORD")


class YamlValueConfig:
    YAML_MAPPINGS = {}
    YAML_TRANSFORMATION_CONFIGS = {}
    setting_utils.load_yaml_mappings(AppConfig.YAML_MAPPINGS_DIR, YAML_MAPPINGS)
    setting_utils.load_yaml_mappings(AppConfig.YAML_TRANSFORMATION_CONFIGS_DIR, YAML_TRANSFORMATION_CONFIGS)
    # with open(AppConfig.YAML_CONFIG_DIR / "product.yaml", 'r', encoding='utf-8') as f:
    #     MAGENTO_DATA_MAPPINGS = yaml.safe_load(f)


# print(json.dumps(YamlValueConfig.YAML_TRANSFORMATION_CONFIGS, indent=4))
