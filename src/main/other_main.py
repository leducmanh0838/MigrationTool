import json

import yaml

from config.settings import AppConfig

with open(AppConfig.YAML_CONFIG_DIR / "magento_data_mappings.yaml", 'r', encoding='utf-8') as f:
    mapping_data = yaml.safe_load(f)
    print(json.dumps(mapping_data, indent=4))
