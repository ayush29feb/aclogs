import typer
from gym_tracker.commands import exercise, workout, block, sets

app = typer.Typer(help="Gym workout logger.")


# invoke_without_command=True required: Typer 0.24+ raises RuntimeError on a
# plain Typer() with no commands registered. Can be removed once subapps are added.
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    pass


app.add_typer(exercise.app, name="exercise")
app.add_typer(workout.app, name="workout")
app.add_typer(block.app, name="block")
app.add_typer(sets.app, name="set")

if __name__ == "__main__":
    app()
