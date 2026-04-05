import json
from gym_tracker.main import app


def _log_set(runner, gym_env, exercise_name, weight, reps, rpe=None, date="2026-03-05"):
    """Helper: create workout, block, exercise (or reuse), log one set."""
    # Add exercise (ignore error if exists)
    er = runner.invoke(app, ["exercise", "add", "--name", exercise_name], env=gym_env)
    if er.exit_code == 0:
        eid = json.loads(er.output)["id"]
    else:
        # Already exists — list to find id
        lr = runner.invoke(app, ["exercise", "list"], env=gym_env)
        exercises = json.loads(lr.output)
        eid = next(e["id"] for e in exercises if e["name"] == exercise_name)

    wr = runner.invoke(app, ["workout", "add", "--name", f"W-{date}", "--date", date], env=gym_env)
    wid = json.loads(wr.output)["id"]
    br = runner.invoke(app, ["block", "add", "--workout-id", str(wid), "--name", "Block B", "--order", "1"], env=gym_env)
    bid = json.loads(br.output)["id"]
    args = ["set", "add", "--block-id", str(bid), "--exercise-id", str(eid), "--round", "1",
            "--weight", str(weight), "--reps", str(reps)]
    if rpe:
        args += ["--rpe", str(rpe)]
    runner.invoke(app, args, env=gym_env)
    return eid


def test_progress_history(runner, gym_env):
    _log_set(runner, gym_env, "Back Squat", 135, 3, date="2026-03-05")
    _log_set(runner, gym_env, "Back Squat", 155, 3, date="2026-03-19")
    result = runner.invoke(app, ["progress", "Back Squat"], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["exercise"] == "Back Squat"
    assert len(data["history"]) == 2
    assert data["history"][0]["date"] <= data["history"][1]["date"]


def test_progress_prs(runner, gym_env):
    _log_set(runner, gym_env, "Back Squat", 135, 3, date="2026-03-05")
    _log_set(runner, gym_env, "Back Squat", 155, 3, date="2026-03-19")
    _log_set(runner, gym_env, "Back Squat", 125, 5, date="2026-03-19")
    result = runner.invoke(app, ["progress", "Back Squat"], env=gym_env)
    data = json.loads(result.output)
    # PR for 3 reps should be 155
    assert data["prs"]["3"]["weight_lbs"] == 155.0
    # PR for 5 reps should be 125
    assert data["prs"]["5"]["weight_lbs"] == 125.0


def test_progress_related(runner, gym_env):
    eid1 = _log_set(runner, gym_env, "KB RDL", 44, 8, date="2026-03-05")
    eid2 = _log_set(runner, gym_env, "DB RDL", 35, 10, date="2026-03-19")
    # Relate them
    runner.invoke(app, ["exercise", "relate", "--exercise-id", str(eid1), "--related-id", str(eid2)], env=gym_env)
    result = runner.invoke(app, ["progress", "KB RDL", "--related"], env=gym_env)
    data = json.loads(result.output)
    exercise_names = [h["exercise"] for h in data["history"]]
    assert "KB RDL" in exercise_names
    assert "DB RDL" in exercise_names


def test_progress_not_found(runner, gym_env):
    result = runner.invoke(app, ["progress", "Nonexistent Exercise"], env=gym_env)
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert "error" in data
