import typer

app = typer.Typer(help="Gym workout logger.")

# Subapps registered after individual command modules are created.
# Placeholder so the entry point resolves now.

if __name__ == "__main__":
    app()
