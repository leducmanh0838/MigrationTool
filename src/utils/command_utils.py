from pathlib import Path

import typer
import yaml

from src.utils.yaml_lookup import CONNECTOR_CLASSES


def update_connector_args(source_config, new_args):
    if connector_name in data['connectors']:
        # Dùng .update() để cập nhật nhiều giá trị cùng lúc
        data['connectors'][connector_name]['args'].update(new_args)
        print(f"Đã cập nhật xong cho {connector_name}")
    else:
        print("Không tìm thấy connector này")


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


def apply_connector(platform_name, config, path):
    platform_config = validate_connector(platform_name, config)
    connector_class_name = platform_config.get('class')
    constructor_args = platform_config.get('args')
    labels = platform_config.get('labels')

    # for key, value in sinh_vien.items():

    for key, value in constructor_args.items():
        if not value:
            typer.secho(
                f"Error: '{platform_name}' not configured.",
                fg=typer.colors.RED,
                bold=True
            )
            raise typer.Exit(code=1)
            # new_value = typer.prompt(f"{labels.get(key)}", hide_input=True)
            # config['connectors'][platform_name]['args'][key] = new_value
            # with open(path, "w", encoding="utf-8") as f:
            #     yaml.dump(config, f, default_flow_style=False)

    # def load_cli_settings(config_path: Path):
    #     """Đọc file YAML và trả về dict"""
    #     if config_path.exists():
    #         with open(config_path, "r", encoding="utf-8") as f:
    #             return yaml.safe_load(f) or {}
    #     return {}
    # connector_class = CONNECTOR_CLASSES.get(connector_class_name)
    # if connector_class:
    #     connector_instance = connector_class(**constructor_args)
    #     print(f"Đã tạo: {type(connector_instance)}")


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
            # print("platform_upper: ", platform_upper)
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
