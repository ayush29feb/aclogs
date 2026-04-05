import json
import typer
from gym_tracker.db import get_session
from gym_tracker.models import Exercise, ExerciseRelation, Set, Block, Workout

app = typer.Typer()


@app.command(name="show")
def show(
    exercise_name: str = typer.Argument(...),
    related: bool = typer.Option(False, "--related", help="Include related exercise variants"),
):
    with get_session() as session:
        exercise = session.query(Exercise).filter(Exercise.name == exercise_name).first()
        if not exercise:
            typer.echo(json.dumps({"error": f"Exercise '{exercise_name}' not found"}))
            raise typer.Exit(1)

        exercise_ids = [exercise.id]

        if related:
            forward = session.query(ExerciseRelation).filter(
                ExerciseRelation.exercise_id == exercise.id
            ).all()
            reverse = session.query(ExerciseRelation).filter(
                ExerciseRelation.related_exercise_id == exercise.id
            ).all()
            exercise_ids += [r.related_exercise_id for r in forward]
            exercise_ids += [r.exercise_id for r in reverse]
            exercise_ids = list(set(exercise_ids))

        rows = (
            session.query(Set, Exercise.name.label("exercise_name"), Workout.date)
            .join(Block, Set.block_id == Block.id)
            .join(Workout, Block.workout_id == Workout.id)
            .join(Exercise, Set.exercise_id == Exercise.id)
            .filter(Set.exercise_id.in_(exercise_ids))
            .order_by(Workout.date)
            .all()
        )

        prs: dict[int, dict] = {}
        history = []
        for s, ex_name, w_date in rows:
            history.append({
                "date": str(w_date),
                "exercise": ex_name,
                "weight_lbs": s.weight_lbs,
                "reps": s.reps,
                "rpe": s.rpe,
                "watts": s.watts,
                "calories": s.calories,
                "duration_secs": s.duration_secs,
            })
            if s.reps and s.weight_lbs:
                key = s.reps
                if key not in prs or s.weight_lbs > prs[key]["weight_lbs"]:
                    prs[key] = {"weight_lbs": s.weight_lbs, "date": str(w_date)}

        typer.echo(json.dumps({
            "exercise": exercise_name,
            "history": history,
            "prs": {str(k): v for k, v in prs.items()},
        }))
