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
    return {"GYM": str(tmp_path)}


@pytest.fixture
def runner():
    return CliRunner()
