import json
from typing import Optional
import typer
from gym_tracker.db import get_session
from gym_tracker.models import Set

app = typer.Typer()


@app.command()
def add(
    block_id: int = typer.Option(..., "--block-id"),
    exercise_id: int = typer.Option(..., "--exercise-id"),
    round_num: int = typer.Option(..., "--round"),
    weight: Optional[float] = typer.Option(None, "--weight"),
    reps: Optional[int] = typer.Option(None, "--reps"),
    rpe: Optional[float] = typer.Option(None, "--rpe"),
    duration: Optional[int] = typer.Option(None, "--duration", help="seconds"),
    distance: Optional[float] = typer.Option(None, "--distance", help="meters"),
    calories: Optional[float] = typer.Option(None, "--calories"),
    watts: Optional[float] = typer.Option(None, "--watts"),
    notes: Optional[str] = typer.Option(None, "--notes"),
):
    with get_session() as session:
        s = Set(
            block_id=block_id,
            exercise_id=exercise_id,
            round=round_num,
            weight_lbs=weight,
            reps=reps,
            rpe=rpe,
            duration_secs=duration,
            distance_m=distance,
            calories=calories,
            watts=watts,
            notes=notes,
        )
        session.add(s)
        session.flush()
        session.refresh(s)
        typer.echo(json.dumps({
            "id": s.id,
            "block_id": s.block_id,
            "exercise_id": s.exercise_id,
            "round": s.round,
            "weight_lbs": s.weight_lbs,
            "reps": s.reps,
            "rpe": s.rpe,
            "duration_secs": s.duration_secs,
            "distance_m": s.distance_m,
            "calories": s.calories,
            "watts": s.watts,
            "notes": s.notes,
            "logged_at": s.logged_at.isoformat() if s.logged_at else None,
        }))


@app.command()
def delete(set_id: int = typer.Argument(...)):
    with get_session() as session:
        s = session.get(Set, set_id)
        if not s:
            typer.echo(json.dumps({"error": f"Set {set_id} not found"}))
            raise typer.Exit(1)
        session.delete(s)
        session.flush()
        typer.echo(json.dumps({"deleted": set_id}))
