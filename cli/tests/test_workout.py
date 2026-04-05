import json
from datetime import date
from gym_tracker.main import app


def test_workout_add(runner, gym_env):
    result = runner.invoke(app, [
        "workout", "add",
        "--name", "MPA Squad W9 Lower",
        "--date", "2026-03-05",
        "--sleep", "1.5",
        "--tag", "squad", "--tag", "lower",
        "--notes", "Good session",
    ], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["name"] == "MPA Squad W9 Lower"
    assert data["date"] == "2026-03-05"
    assert data["sleep_hours"] == 1.5
    assert data["tags"] == ["squad", "lower"]


def test_workout_list(runner, gym_env):
    runner.invoke(app, ["workout", "add", "--name", "Session A", "--date", "2026-03-05"], env=gym_env)
    runner.invoke(app, ["workout", "add", "--name", "Session B", "--date", "2026-03-10"], env=gym_env)
    result = runner.invoke(app, ["workout", "list"], env=gym_env)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
    # newest first
    assert data[0]["date"] == "2026-03-10"


def test_workout_list_filter_by_tag(runner, gym_env):
    runner.invoke(app, ["workout", "add", "--name", "A", "--date", "2026-03-05", "--tag", "upper"], env=gym_env)
    runner.invoke(app, ["workout", "add", "--name", "B", "--date", "2026-03-10", "--tag", "lower"], env=gym_env)
    result = runner.invoke(app, ["workout", "list", "--tag", "upper"], env=gym_env)
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "A"


def test_workout_show_empty_blocks(runner, gym_env):
    r = runner.invoke(app, ["workout", "add", "--name", "A", "--date", "2026-03-05"], env=gym_env)
    wid = json.loads(r.output)["id"]
    result = runner.invoke(app, ["workout", "show", str(wid)], env=gym_env)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == wid
    assert data["blocks"] == []


def test_workout_delete(runner, gym_env):
    r = runner.invoke(app, ["workout", "add", "--name", "A", "--date", "2026-03-05"], env=gym_env)
    wid = json.loads(r.output)["id"]
    result = runner.invoke(app, ["workout", "delete", str(wid)], env=gym_env)
    assert result.exit_code == 0
    list_result = runner.invoke(app, ["workout", "list"], env=gym_env)
    assert json.loads(list_result.output) == []
