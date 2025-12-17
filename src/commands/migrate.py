import typer

app = typer.Typer()

# def migrate_main(source: str, destination: str, entity: str = "product"):
#     typer.echo(f"🚀 Chạy migrate cho {entity} từ {source} sang {destination}")

@app.command("run")
def run(source, destination):
    print(f"Migrating {source} to {destination}")

# @app.command("makemigrations")
# def makemigrations():
#     print("Creating migrations...")