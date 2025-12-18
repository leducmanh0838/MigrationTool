import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    source: str,
    destination: str,
    entity: Annotated[str, typer.Argument()] = "product"
):
    """Chạy tiến trình di chuyển dữ liệu"""
    conf = state["config"]
    path = state["config_path"]

    # Logic xử lý key (giống code cũ của bạn)
    # ...
    typer.secho(f"🚀 Bắt đầu migrate {entity} từ {source} sang {destination}", fg="green")