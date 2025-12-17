# import typer
# from typing import Optional
# from typing_extensions import Annotated
#
# # Giả sử bạn import các service từ cấu trúc src của mình
# # from src.services.migration_service import MigrationService
#
# app = typer.Typer(help="Công cụ chuyển đổi dữ liệu (Migration Tool)")
#
#
# @app.command()
# def migrate(
#         source: Annotated[str, typer.Argument(help="Nền tảng nguồn (ví dụ: magento, shopify)")],
#         destination: Annotated[str, typer.Argument(help="Nền tảng đích (ví dụ: woo, bigcommerce)")],
#         # entity: Annotated[str, typer.Argument(help="Thực thể cần migrate (product, customer, order)")],
#         # source_key: Annotated[Optional[str], typer.Option(envvar="SOURCE_API_KEY", help="API Key nguồn")] = None,
#         # dest_key: Annotated[Optional[str], typer.Option(envvar="DEST_API_KEY", help="API Key đích")] = None,
#         limit: Annotated[int, typer.Option(help="Giới hạn số lượng bản ghi")] = 100
# ):
#     """
#     Thực hiện di chuyển dữ liệu giữa các nền tảng.
#     """
#     typer.echo(f"🚀 Bắt đầu migrate từ {source} sang {destination}...")
#
#     # if not source_key or not dest_key:
#     #     typer.secho("⚠️ Cảnh báo: Thiếu API Key, sẽ sử dụng cấu hình mặc định từ config/settings.py",
#     #                 fg=typer.colors.YELLOW)
#
#     # Đây là nơi bạn gọi MigrationService của mình
#     # service = MigrationService(source, destination, source_key, dest_key)
#     # service.run(entity, limit)
#
#     typer.secho(f"✅ Hoàn thành migrate!", fg=typer.colors.GREEN, bold=True)
#
#
# @app.command()
# def check_connection():
#     """Kiểm tra kết nối tới các nền tảng đã cấu hình."""
#     typer.echo("🔍 Đang kiểm tra kết nối...")
#
# """
# python manage.py
# """
#
#
# if __name__ == "__main__":
#     app()
import typer
import yaml
from pathlib import Path
from typing_extensions import Annotated

app = typer.Typer(rich_markup_mode="rich")

# Đường dẫn file cấu hình tùy chỉnh của bạn
DEFAULT_CONFIG_PATH = Path("config/cli_settings.yaml")

# Biến global để chứa dữ liệu cấu hình sau khi load
state = {"config": {}}

def load_settings(config_path: Path):
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

@app.callback()
def main(
    config: Annotated[str, typer.Option("--config", "-c", help="Đường dẫn file cấu hình")] = str(DEFAULT_CONFIG_PATH)
):
    """
    [bold green]Migration Tool CLI[/bold green]
    """
    path = Path(config)
    state["config_path"] = path
    state["config"] = load_settings(path)

@app.command()
def migrate(
    source: str,
    destination: str,
    entity: Annotated[str, typer.Argument()] = "product"
):
    """Chạy tiến trình di chuyển dữ liệu"""
    conf = state["config"]
    path = state["config_path"]

    # 1. Kiểm tra Key cho nguồn (source)
    s_key = conf.get(f"{source}_key")
    if not s_key:
        s_key = typer.prompt(f"🔑 Chưa có Key cho {source.upper()}. Vui lòng nhập", hide_input=True)
        conf[f"{source}_key"] = s_key
        save_settings(path, conf)

    # 2. Kiểm tra Key cho đích (destination)
    d_key = conf.get(f"{destination}_key")
    if not d_key:
        d_key = typer.prompt(f"🔑 Chưa có Key cho {destination.upper()}. Vui lòng nhập", hide_input=True)
        conf[f"{destination}_key"] = d_key
        save_settings(path, conf)

    typer.secho(f"\n🚀 Cấu hình hoàn tất! Bắt đầu migrate {entity}...", fg="green")
    typer.echo(f"--- Thông tin ---")
    typer.echo(f"Nguồn: {source} (Key: ****{s_key[-4:] if s_key else ''})")
    typer.echo(f"Đích:  {destination} (Key: ****{d_key[-4:] if d_key else ''})")
    typer.echo(f"File cấu hình: {path}")


@app.command()
def config(
        platform: Annotated[str, typer.Argument(help="Nền tảng cần cấu hình lại (magento/woo)")],
        key: Annotated[str, typer.Option("--key", "-k", help="API Key mới")] = None
):
    """
    Cập nhật hoặc xem cấu hình của một nền tảng.
    """
    conf = load_settings(state["config_path"])

    # Nếu người dùng không truyền --key, thì dùng prompt để hỏi
    new_key = key if key else typer.prompt(f"🔑 Nhập API Key mới cho {platform}", hide_input=True)

    conf[f"{platform}_key"] = new_key
    save_settings(state["config_path"], conf)

    typer.secho(f"✅ Đã cập nhật cấu hình cho {platform}!", fg="green")

if __name__ == "__main__":
    app()