import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gym_tracker.models import Base

_engine = None


def get_db_path() -> Path:
    gym_root = os.environ.get("GYM")
    if not gym_root:
        raise RuntimeError("GYM environment variable not set. Run: export GYM=$(git rev-parse --show-toplevel)")
    return Path(gym_root) / "data" / "gym.db"


def get_engine():
    global _engine
    if _engine is None:
        db_path = get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(_engine)
    return _engine


@contextmanager
def get_session():
    with Session(get_engine()) as session:
        yield session
        session.commit()
