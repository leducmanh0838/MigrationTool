import typer

app = typer.Typer()

@app.command("set")
def config_set(platform: str, key: str):
    typer.echo(f"✅ Key for {platform} updated.")

@app.command("show")
def config_show():
    typer.echo("📜 Current configurations...")