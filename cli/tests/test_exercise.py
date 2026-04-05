import json
from gym_tracker.main import app


def test_exercise_add(runner, gym_env):
    result = runner.invoke(app, ["exercise", "add", "--name", "Back Squat", "--muscle-group", "legs"], env=gym_env)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["name"] == "Back Squat"
    assert data["muscle_group"] == "legs"
    assert "id" in data


def test_exercise_add_duplicate_fails(runner, gym_env):
    runner.invoke(app, ["exercise", "add", "--name", "Back Squat"], env=gym_env)
    result = runner.invoke(app, ["exercise", "add", "--name", "Back Squat"], env=gym_env)
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert "error" in data


def test_exercise_list(runner, gym_env):
    runner.invoke(app, ["exercise", "add", "--name", "Back Squat"], env=gym_env)
    runner.invoke(app, ["exercise", "add", "--name", "Deadlift"], env=gym_env)
    result = runner.invoke(app, ["exercise", "list"], env=gym_env)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
    assert data[0]["name"] == "Back Squat"


def test_exercise_relate(runner, gym_env):
    r1 = runner.invoke(app, ["exercise", "add", "--name", "KB RDL"], env=gym_env)
    r2 = runner.invoke(app, ["exercise", "add", "--name", "DB RDL"], env=gym_env)
    id1 = json.loads(r1.output)["id"]
    id2 = json.loads(r2.output)["id"]
    result = runner.invoke(app, ["exercise", "relate", "--exercise-id", str(id1), "--related-id", str(id2)], env=gym_env)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["relation_type"] == "variant"
