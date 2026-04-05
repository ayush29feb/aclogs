import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gym_tracker.models import Base


def get_db_path() -> Path:
    gym_root = os.environ.get("GYM")
    if not gym_root:
        raise RuntimeError("GYM environment variable not set. Run: export GYM=$(git rev-parse --show-toplevel)")
    return Path(gym_root) / "data" / "gym.db"


def get_engine():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}")


@contextmanager
def get_session():
    engine = get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
