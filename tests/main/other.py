# python tests/main/other.py
from rich.console import Console
import time

console = Console()

with console.status("[bold blue]Migrating products..."):
    time.sleep(3)

console.print("[green]✔ Done[/green]")
from rich.progress import track
import time

for item in track(range(100), description="Migrating orders"):
    time.sleep(0.02)


# from rich.progress import Progress
# import time
# with Progress() as progress:
#     task = progress.add_task("Migrating products", total=200)
#
#     for i in range(200):
#         time.sleep(0.02)
#         progress.update(task, advance=1)
#         print(i)



# from rich.logging import RichHandler
# import logging
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(message)s",
#     handlers=[RichHandler()]
# )
#
# logger = logging.getLogger("migration")
#
# logger.info("Start migration")
# logger.error("Order failed")



# from rich.table import Table
# from rich.console import Console
#
# console = Console()
#
# table = Table(title="Migration Summary")
# table.add_column("Type")
# table.add_column("Success")
# table.add_column("Failed")
#
# table.add_row("Products", "120", "2")
# table.add_row("Orders", "80", "1")
#
# console.print(table)
