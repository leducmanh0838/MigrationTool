#  python manage.py

import typer
from pathlib import Path
from typing_extensions import Annotated

from config.settings import AppConfig
from src.connectors.abstract.base_read_connector import BaseReadConnector
from src.connectors.abstract.base_write_connector import BaseWriteConnector
from src.services.migration_service import MigrationService
from src.ui_handlers.rich_migration_ui_handler import RichMigrationUIHandler
from src.utils import command_utils
import time
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
def migrate(source: str, target: str,
            # entity: Annotated[str, typer.Argument()] = "product"
            ):
    """Chạy tiến trình di chuyển dữ liệu"""
    conf = state["config"]
    path = state["config_path"]

    read_connector = command_utils.apply_connector(source, conf, path)
    write_connector = command_utils.apply_connector(target, conf, path)

    if not isinstance(read_connector, BaseReadConnector):
        typer.echo(f"{read_connector.__name__} must inherit from BaseReadConnector")
        raise typer.Exit(code=1)

    if not isinstance(write_connector, BaseWriteConnector):
        typer.echo(f"{write_connector.__name__} must inherit from BaseWriteConnector")
        raise typer.Exit(code=1)

    current_migration_id = conf.get('current_migration_id')
    service = MigrationService(write_connector=write_connector,
                               read_connector=read_connector,
                               migration_id=current_migration_id,
                               migration_path=['category'],
                               ui_handler=RichMigrationUIHandler())

    command_utils.config_migration_cli_settings(service.migration_id, conf, path)
    service.run_migration()


@app.command()
def config(platform: Annotated[str, typer.Argument(help="Config platform")], ):
    conf = state["config"]
    path = state["config_path"]
    command_utils.config_connector_cli_settings(platform, conf, path)


from rich.console import Console

console = Console()

@app.command()
def test():
    with console.status("[bold blue]Migrating products..."):
        time.sleep(3)

    console.print("[green]✔ Done[/green]")
    from rich.progress import track

    for item in track(range(100), description="Migrating orders"):
        time.sleep(0.02)

if __name__ == "__main__":
    app()

# python manage.py
