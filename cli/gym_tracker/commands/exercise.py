import json
import typer
from sqlalchemy.exc import IntegrityError
from gym_tracker.db import get_session
from gym_tracker.models import Exercise, ExerciseRelation

app = typer.Typer()


@app.command()
def add(
    name: str = typer.Option(..., "--name"),
    muscle_group: str = typer.Option(None, "--muscle-group"),
    notes: str = typer.Option(None, "--notes"),
):
    with get_session() as session:
        exercise = Exercise(name=name, muscle_group=muscle_group, notes=notes)
        session.add(exercise)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            typer.echo(json.dumps({"error": f"Exercise '{name}' already exists"}))
            raise typer.Exit(1)
        session.refresh(exercise)
        typer.echo(json.dumps({
            "id": exercise.id,
            "name": exercise.name,
            "muscle_group": exercise.muscle_group,
            "notes": exercise.notes,
        }))


@app.command(name="list")
def list_exercises():
    with get_session() as session:
        exercises = session.query(Exercise).order_by(Exercise.name).all()
        typer.echo(json.dumps([{
            "id": e.id,
            "name": e.name,
            "muscle_group": e.muscle_group,
            "notes": e.notes,
        } for e in exercises]))


@app.command()
def relate(
    exercise_id: int = typer.Option(..., "--exercise-id"),
    related_id: int = typer.Option(..., "--related-id"),
    relation_type: str = typer.Option("variant", "--type"),
):
    if exercise_id == related_id:
        typer.echo(json.dumps({"error": "Cannot relate an exercise to itself"}))
        raise typer.Exit(1)
    with get_session() as session:
        relation = ExerciseRelation(
            exercise_id=exercise_id,
            related_exercise_id=related_id,
            relation_type=relation_type,
        )
        session.add(relation)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            typer.echo(json.dumps({"error": "Relation already exists or invalid exercise ID"}))
            raise typer.Exit(1)
        typer.echo(json.dumps({
            "exercise_id": exercise_id,
            "related_exercise_id": related_id,
            "relation_type": relation_type,
        }))
