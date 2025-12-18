from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, MofNCompleteColumn

from src.ui_handlers.abstract.base_migration_ui_handler import BaseMigrationUIHandler

console = Console()

class RichMigrationUIHandler(BaseMigrationUIHandler):
    def __init__(self):
        self.console = console

    def info(self, message: str):
        self.console.print(f"[bold blue]🔹 INFO:[/bold blue] {message}")

    def success(self, message: str):
        self.console.print(f"[bold green]✅ SUCCESS:[/bold green] {message}")

    def warning(self, message: str):
        self.console.print(f"[bold yellow]⚠️  WARNING:[/bold yellow] {message}")

    def error(self, message: str, error_detail: str = ""):
        content = f"[bold white]{message}[/bold white]"
        if error_detail:
            content += f"\n[dim]Detail: {error_detail}[/dim]"
        self.console.print(Panel(content, title="[bold red]✘ ERROR[/bold red]", border_style="red"))

    def track_progress(self, name: str, total: int):
        # Trả về một đối tượng Progress của Rich để quản lý việc render thanh tiến trình
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[bold cyan]{name}"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),  # Hiển thị x/y (số lượng hiện tại / tổng)
            TaskProgressColumn(),
            console=self.console,
            transient=True  # Thanh progress sẽ biến mất sau khi xong để log sạch sẽ
        )

    def finish_migration(self, summary_data: list):
        table = Table(title="\n📊 TỔNG KẾT MIGRATION", title_style="bold magenta", expand=True)
        table.add_column("Thực thể", style="cyan")
        table.add_column("Trạng thái", justify="center")
        table.add_column("Tiến độ", justify="right")
        table.add_column("Thời gian", justify="right", style="dim")

        for item in summary_data:
            # Logic xác định màu sắc trạng thái
            if item['current'] == item['total']:
                status = "[green]Thành công[/green]"
                progress_style = "green"
            elif item['current'] > 0:
                status = "[yellow]Dở dang[/yellow]"
                progress_style = "yellow"
            else:
                status = "[red]Thất bại[/red]"
                progress_style = "red"

            table.add_row(
                item['name'],
                status,
                f"[{progress_style}]{item['current']}/{item['total']}[/{progress_style}]",
                f"{item['time']}s"
            )

        self.console.print(table)
