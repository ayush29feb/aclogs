import json
from typing import Optional
import typer
from gym_tracker.db import get_session
from gym_tracker.models import Block

app = typer.Typer()


@app.command()
def add(
    workout_id: int = typer.Option(..., "--workout-id"),
    name: str = typer.Option(..., "--name"),
    order: int = typer.Option(..., "--order"),
    scheme: Optional[str] = typer.Option(None, "--scheme"),
):
    with get_session() as session:
        block = Block(workout_id=workout_id, name=name, order=order, scheme=scheme)
        session.add(block)
        session.flush()
        session.refresh(block)
        typer.echo(json.dumps({
            "id": block.id,
            "workout_id": block.workout_id,
            "name": block.name,
            "order": block.order,
            "scheme": block.scheme,
        }))
