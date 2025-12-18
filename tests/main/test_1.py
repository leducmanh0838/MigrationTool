import time
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, MofNCompleteColumn

console = Console()


class BaseMigrationUIHandler:
    def info(self, message: str): pass

    def success(self, message: str): pass

    def warning(self, message: str): pass

    def error(self, message: str, error_detail: str = ""): pass

    def track_progress(self, name: str, total: int): pass  # Trả về context progress

    def finish_migration(self, summary_data: list): pass


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


class MigrationService:
    def __init__(self, ui: BaseMigrationUIHandler):
        self.ui = ui

    def run_all(self):
        self.ui.info("Khởi động quy trình migrate...")
        summary = []
        entities = [
            {"name": "Categories", "count": 150},
            {"name": "Products", "count": 1200},
            {"name": "Customers", "count": 500},
            {"name": "Orders", "count": 2000}
        ]

        for entity in entities:
            start_time = time.time()
            current_processed = 0
            error_count = 0
            last_error = ""

            with self.ui.track_progress(entity['name'], entity['count']) as progress:
                task = progress.add_task("migrate", total=entity['count'])

                # Vòng lặp xử lý từng bản ghi
                for i in range(entity['count']):
                    try:
                        # Giả lập logic xử lý
                        time.sleep(0.002)

                        # GIẢ LẬP LỖI tại vị trí 350 (index 349 hoặc 350 tùy cách đếm)
                        if entity['name'] == "Customers" and i == 350:
                            raise Exception(f"Lỗi dữ liệu tại bản ghi thứ {i}")

                        # Nếu thành công thì tăng biến đếm
                        current_processed += 1

                    except Exception as e:
                        error_count += 1
                        last_error = str(e)
                        # In lỗi ra console ngay lập tức nếu muốn, hoặc chỉ ghi log
                        # self.ui.error(f"Lỗi bản ghi {i}", error_detail=last_error)

                    # Luôn cập nhật thanh progress bất kể thành công hay thất bại
                    progress.update(task, advance=1)

                # Sau khi chạy hết vòng lặp (đã chạy đến 500/500)
                if error_count == 0:
                    self.ui.success(f"Hoàn thành trọn vẹn {entity['name']}")
                else:
                    self.ui.warning(
                        f"Hoàn thành {entity['name']} với {error_count} lỗi (Thành công {current_processed}/{entity['count']})")

            duration = round(time.time() - start_time, 2)

            # Xác định trạng thái tổng quát để đưa vào bảng kết quả
            final_status = "ok" if error_count == 0 else "partial"

            summary.append({
                "name": entity['name'],
                "status": final_status,
                "total": entity['count'],
                "current": current_processed,
                "time": duration
            })

        self.ui.finish_migration(summary)


if __name__ == "__main__":
    handler = RichMigrationUIHandler()
    service = MigrationService(ui=handler)
    service.run_all()
