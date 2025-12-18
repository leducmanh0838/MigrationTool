# state.py
import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("config/cli_settings.yaml")
state = {"config": {}, "config_path": DEFAULT_CONFIG_PATH}

def load_settings(config_path: Path):
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_settings(config_path: Path, data: dict):
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)