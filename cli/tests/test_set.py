import json
from gym_tracker.main import app


def _setup(runner, gym_env):
    """Create workout, block, and exercise. Returns (workout_id, block_id, exercise_id)."""
    wr = runner.invoke(app, ["workout", "add", "--name", "W1", "--date", "2026-03-05"], env=gym_env)
    wid = json.loads(wr.output)["id"]
    br = runner.invoke(app, ["block", "add", "--workout-id", str(wid), "--name", "Block B", "--order", "1"], env=gym_env)
    bid = json.loads(br.output)["id"]
    er = runner.invoke(app, ["exercise", "add", "--name", "Back Squat"], env=gym_env)
    eid = json.loads(er.output)["id"]
    return wid, bid, eid


def test_set_add_strength(runner, gym_env):
    wid, bid, eid = _setup(runner, gym_env)
    result = runner.invoke(app, [
        "set", "add",
        "--block-id", str(bid),
        "--exercise-id", str(eid),
        "--round", "1",
        "--weight", "135",
        "--reps", "3",
        "--rpe", "8",
    ], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["weight_lbs"] == 135.0
    assert data["reps"] == 3
    assert data["rpe"] == 8.0


def test_set_add_cardio(runner, gym_env):
    wid, bid, _ = _setup(runner, gym_env)
    er = runner.invoke(app, ["exercise", "add", "--name", "C2 Bike"], env=gym_env)
    eid = json.loads(er.output)["id"]
    result = runner.invoke(app, [
        "set", "add",
        "--block-id", str(bid),
        "--exercise-id", str(eid),
        "--round", "1",
        "--duration", "330",
        "--calories", "81",
        "--watts", "168",
    ], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["calories"] == 81.0
    assert data["watts"] == 168.0


def test_set_superset(runner, gym_env):
    """Two exercises in same round = superset."""
    wid, bid, eid1 = _setup(runner, gym_env)
    er2 = runner.invoke(app, ["exercise", "add", "--name", "Push-up"], env=gym_env)
    eid2 = json.loads(er2.output)["id"]
    runner.invoke(app, ["set", "add", "--block-id", str(bid), "--exercise-id", str(eid1), "--round", "1", "--reps", "12"], env=gym_env)
    runner.invoke(app, ["set", "add", "--block-id", str(bid), "--exercise-id", str(eid2), "--round", "1", "--reps", "15"], env=gym_env)
    # Verify workout show groups them by round
    result = runner.invoke(app, ["workout", "show", str(wid)], env=gym_env)
    data = json.loads(result.output)
    round_1 = data["blocks"][0]["rounds"]["1"]
    assert len(round_1) == 2


def test_set_delete(runner, gym_env):
    wid, bid, eid = _setup(runner, gym_env)
    r = runner.invoke(app, ["set", "add", "--block-id", str(bid), "--exercise-id", str(eid), "--round", "1", "--reps", "5"], env=gym_env)
    sid = json.loads(r.output)["id"]
    result = runner.invoke(app, ["set", "delete", str(sid)], env=gym_env)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["deleted"] == sid
