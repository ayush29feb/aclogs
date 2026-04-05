import pytest
from sqlalchemy import create_engine
from typer.testing import CliRunner

from gym_tracker.models import Base


@pytest.fixture
def gym_env(tmp_path):
    """Temp dir with initialized SQLite DB. Pass as env= to runner.invoke()."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    engine = create_engine(f"sqlite:///{data_dir}/gym.db")
    Base.metadata.create_all(engine)
    engine.dispose()
    return {"GYM": str(tmp_path)}


@pytest.fixture(autouse=True)
def reset_engine():
    """Reset the db engine singleton between tests so each test gets a fresh DB."""
    import gym_tracker.db as db_module
    db_module._engine = None
    yield
    db_module._engine = None


@pytest.fixture
def runner():
    return CliRunner()
