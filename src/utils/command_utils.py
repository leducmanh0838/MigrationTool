from pathlib import Path

import typer
import yaml

from src.connectors.abstract.base_connector import BaseConnector
from src.utils.yaml_lookup import CONNECTOR_CLASSES


def config_connector_cli_settings(platform_name, config, path):
    platform_config = validate_connector(platform_name, config)
    constructor_args = platform_config.get('args')
    labels = platform_config.get('labels')
    for key, value in constructor_args.items():
        new_value = typer.prompt(f"{labels.get(key)}", hide_input=True)
        config['connectors'][platform_name]['args'][key] = new_value
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)
    typer.secho(f"Configuration for {platform_name} has been updated.", fg="green")


def config_migration_cli_settings(migration_id, config, path):
    config['current_migration_id'] = migration_id
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)
    if migration_id:
        typer.secho(f"Migration ID: {migration_id}.", fg="green")


def validate_connector(name: str, config: dict):
    """Hàm bổ trợ để kiểm tra connector có tồn tại không"""
    connector_cfg = config.get("connectors", {}).get(name)
    if not connector_cfg:
        typer.secho(
            f"Error: Connector '{name}' does not exist in the configuration.",
            fg=typer.colors.RED,
            bold=True
        )
        valid_connectors = list(config.get("connectors", {}).keys())
        typer.echo(f"Currently valid connectors: {', '.join(valid_connectors)}")
        raise typer.Exit(code=1)
    return connector_cfg


def apply_connector(platform_name, config, path) -> BaseConnector:
    platform_config = validate_connector(platform_name, config)
    connector_class_name = platform_config.get('class')
    constructor_args = platform_config.get('args')
    labels = platform_config.get('labels')

    for key, value in constructor_args.items():
        if not value:
            typer.secho(
                f"Error: '{platform_name}' not configured.",
                fg=typer.colors.RED,
                bold=True
            )
            raise typer.Exit(code=1)

    connector_class = CONNECTOR_CLASSES.get(connector_class_name)
    if not connector_class:
        typer.echo(f"{connector_class.__name__} does not exist")
        raise typer.Exit(code=1)
    if not issubclass(connector_class, BaseConnector):
        typer.echo(f"{connector_class.__name__} must inherit from BaseConnector")
        raise typer.Exit(code=1)
        # raise TypeError(f"{connector_class.__name__} phải kế thừa từ BaseConnector")
    connector_instance = connector_class(**constructor_args)
    is_success, message = connector_instance.check_connection()
    if is_success:
        typer.secho(f"Connected to {platform_name} successfully", fg="green")
    else:
        typer.secho(
            f"Connection to {platform_name} failed: {message}",
            fg=typer.colors.RED,
            bold=True
        )
        raise typer.Exit(code=1)
    return connector_instance


def load_cli_settings(config_path: Path):
    """Đọc file YAML và trả về dict"""
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_settings(config_path: Path, data: dict):
    """Lưu dict vào file YAML"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


def config_platform_key(platform: str, config: dict, config_path: Path):
    platform_lower = platform.lower()
    platform_upper = platform.upper()

    # 1. Đảm bảo tồn tại dictionary cho platform (ví dụ: config['magento'])
    if platform_lower not in config or config[platform_lower] is None:
        config[platform_lower] = {}

    updated = False

    # Danh sách các trường cần thiết
    fields = ["key", "secret"]

    for field in fields:
        # Lấy giá trị hiện tại từ config[platform][field]
        current_value = config[platform_lower].get(field)

        # Nếu chưa có giá trị hoặc giá trị là chuỗi rỗng
        if not current_value or str(current_value).strip() == "":
            prompt_label = "API Key" if field == "key" else "API Secret"
            new_value = typer.prompt(f"Config {prompt_label} for {platform_upper}", hide_input=True)

            # Xử lý: Nếu người dùng để trống -> gán None (null trong YAML)
            if not new_value or new_value.strip() == "":
                config[platform_lower][field] = None
            else:
                config[platform_lower][field] = new_value

            updated = True

    # 2. Lưu nếu có thay đổi
    if updated:
        save_settings(config_path, config)
        typer.secho(f"Đã cập nhật thông tin cho {platform_upper}", fg="green")

    return config[platform_lower].get("key"), config[platform_lower].get("secret")
