import os
import pytest
from gym_tracker.db import get_db_path


def test_db_init_requires_gym_env():
    old = os.environ.pop("GYM", None)
    try:
        with pytest.raises(RuntimeError, match="GYM environment variable not set"):
            get_db_path()
    finally:
        if old:
            os.environ["GYM"] = old
