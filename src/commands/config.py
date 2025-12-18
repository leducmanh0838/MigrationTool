import typer
from typing_extensions import Annotated

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(
    platform: Annotated[str, typer.Argument(help="Nền tảng cần cấu hình lại")],
    key: Annotated[str, typer.Option("--key", "-k")] = None
):
    """Cập nhật hoặc xem cấu hình"""
    # Logic xử lý config (giống code cũ của bạn)
    # ...
    typer.secho(f"✅ Đã cập nhật cho {platform}", fg="green")