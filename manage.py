#  python manage.py

import typer
from pathlib import Path
from typing_extensions import Annotated

from config.settings import AppConfig
from src.utils import command_utils
from src.utils.yaml_lookup import CONNECTOR_CLASSES

app = typer.Typer(rich_markup_mode="rich")

# Biến global để chứa dữ liệu cấu hình sau khi load
state = {"config": {}}


@app.callback()
def main(
        config: Annotated[str, typer.Option("--config", "-c", help="Đường dẫn file cấu hình")] = str(
            AppConfig.DEFAULT_CLI_VARIABLE_PATH)
):
    """
    [bold green]Migration Tool CLI[/bold green]
    """
    path = Path(config)
    state["config_path"] = path
    state["config"] = command_utils.load_cli_settings(path)


@app.command()
def migrate(
        source: str,
        target: str,
        # entity: Annotated[str, typer.Argument()] = "product"
):
    """Chạy tiến trình di chuyển dữ liệu"""
    conf = state["config"]
    path = state["config_path"]

    # source_config = command_utils.validate_connector(source, conf)
    # target_config = command_utils.validate_connector(target, conf)
    #
    # if source_config:
    command_utils.apply_connector(source, conf, path)
    command_utils.apply_connector(target, conf, path)

    # if not s_key:
    #     command_utils.config_platform_key(source, conf, path)
    #
    # d_key = conf.get(f"{destination}_key")
    # if not d_key:
    #     command_utils.config_platform_key(destination, conf, path)
    #
    # typer.secho(f"\n🚀 Cấu hình hoàn tất! Bắt đầu migrate...", fg="green")
    # typer.echo(f"--- Thông tin ---")
    # typer.echo(f"Nguồn: {source} (Key: ****{s_key[-4:] if s_key else ''})")
    # typer.echo(f"Đích:  {destination} (Key: ****{d_key[-4:] if d_key else ''})")
    # typer.echo(f"File cấu hình: {path}")


@app.command()
def config(
        platform: Annotated[str, typer.Argument(help="Nền tảng cần cấu hình lại (magento/woo)")],
        key: Annotated[str, typer.Option("--key", "-k", help="API Key mới")] = None
):
    """
    Cập nhật hoặc xem cấu hình của một nền tảng.
    """
    conf = command_utils.load_cli_settings(state["config_path"])

    # Nếu người dùng không truyền --key, thì dùng prompt để hỏi
    new_key = key if key else typer.prompt(f"🔑 Nhập API Key mới cho {platform}", hide_input=True)

    conf[f"{platform}_key"] = new_key
    command_utils.save_settings(state["config_path"], conf)

    typer.secho(f"✅ Đã cập nhật cấu hình cho {platform}!", fg="green")


if __name__ == "__main__":
    app()

# python manage.py
