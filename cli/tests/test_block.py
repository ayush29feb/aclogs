import json
from gym_tracker.main import app


def _make_workout(runner, gym_env):
    r = runner.invoke(app, ["workout", "add", "--name", "W1", "--date", "2026-03-05"], env=gym_env)
    return json.loads(r.output)["id"]


def test_block_add(runner, gym_env):
    wid = _make_workout(runner, gym_env)
    result = runner.invoke(app, [
        "block", "add",
        "--workout-id", str(wid),
        "--name", "Block B — Back Squat",
        "--order", "2",
        "--scheme", "6 Sets | RPE 8",
    ], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["name"] == "Block B — Back Squat"
    assert data["order"] == 2
    assert data["workout_id"] == wid


def test_block_shows_in_workout(runner, gym_env):
    wid = _make_workout(runner, gym_env)
    runner.invoke(app, ["block", "add", "--workout-id", str(wid), "--name", "Block A", "--order", "1"], env=gym_env)
    runner.invoke(app, ["block", "add", "--workout-id", str(wid), "--name", "Block B", "--order", "2"], env=gym_env)
    result = runner.invoke(app, ["workout", "show", str(wid)], env=gym_env)
    data = json.loads(result.output)
    assert len(data["blocks"]) == 2
    assert data["blocks"][0]["name"] == "Block A"
    assert data["blocks"][1]["name"] == "Block B"
