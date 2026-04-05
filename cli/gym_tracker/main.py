import typer

app = typer.Typer(help="Gym workout logger.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    pass


if __name__ == "__main__":
    app()
