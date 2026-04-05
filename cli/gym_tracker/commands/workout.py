import json
from datetime import date
from typing import List, Optional
import typer
from sqlalchemy import desc
from gym_tracker.db import get_session
from gym_tracker.models import Workout, Block, Set

app = typer.Typer()


def _serialize_workout(workout: Workout, include_blocks: bool = False) -> dict:
    out = {
        "id": workout.id,
        "name": workout.name,
        "date": str(workout.date),
        "sleep_hours": workout.sleep_hours,
        "tags": workout.tags or [],
        "notes": workout.notes,
        "photo_path": workout.photo_path,
    }
    if include_blocks:
        blocks_out = []
        for block in sorted(workout.blocks, key=lambda b: b.order):
            rounds: dict[int, list] = {}
            for s in block.sets:
                rounds.setdefault(s.round, []).append({
                    "id": s.id,
                    "exercise_id": s.exercise_id,
                    "exercise": s.exercise.name,
                    "weight_lbs": s.weight_lbs,
                    "reps": s.reps,
                    "rpe": s.rpe,
                    "duration_secs": s.duration_secs,
                    "distance_m": s.distance_m,
                    "calories": s.calories,
                    "watts": s.watts,
                    "notes": s.notes,
                    "logged_at": str(s.logged_at),
                })
            blocks_out.append({
                "id": block.id,
                "name": block.name,
                "order": block.order,
                "scheme": block.scheme,
                "rounds": rounds,
            })
        out["blocks"] = blocks_out
    return out


@app.command()
def add(
    name: str = typer.Option(..., "--name"),
    date_str: str = typer.Option(..., "--date", help="YYYY-MM-DD"),
    sleep: Optional[float] = typer.Option(None, "--sleep"),
    tags: List[str] = typer.Option([], "--tag"),
    notes: Optional[str] = typer.Option(None, "--notes"),
    photo: Optional[str] = typer.Option(None, "--photo"),
):
    workout_date = date.fromisoformat(date_str)
    with get_session() as session:
        workout = Workout(
            name=name,
            date=workout_date,
            sleep_hours=sleep,
            tags=tags if tags else None,
            notes=notes,
            photo_path=photo,
        )
        session.add(workout)
        session.flush()
        session.refresh(workout)
        typer.echo(json.dumps(_serialize_workout(workout)))


@app.command()
def show(workout_id: int = typer.Argument(...)):
    with get_session() as session:
        workout = session.get(Workout, workout_id)
        if not workout:
            typer.echo(json.dumps({"error": f"Workout {workout_id} not found"}))
            raise typer.Exit(1)
        typer.echo(json.dumps(_serialize_workout(workout, include_blocks=True), default=str))


@app.command(name="list")
def list_workouts(
    tag: Optional[str] = typer.Option(None, "--tag"),
    limit: int = typer.Option(20, "--limit"),
):
    with get_session() as session:
        workouts = session.query(Workout).order_by(desc(Workout.date)).all()
        if tag:
            workouts = [w for w in workouts if tag in (w.tags or [])]
        workouts = workouts[:limit]
        typer.echo(json.dumps([_serialize_workout(w) for w in workouts]))


@app.command()
def delete(workout_id: int = typer.Argument(...)):
    with get_session() as session:
        workout = session.get(Workout, workout_id)
        if not workout:
            typer.echo(json.dumps({"error": f"Workout {workout_id} not found"}))
            raise typer.Exit(1)
        session.delete(workout)
        typer.echo(json.dumps({"deleted": workout_id}))
