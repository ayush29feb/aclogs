import typer

app = typer.Typer(help="Gym workout logger.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Gym workout logger."""
    if ctx.invoked_subcommand is None:
        pass


# Subapps registered after individual command modules are created.
# Placeholder so the entry point resolves now.

if __name__ == "__main__":
    app()
