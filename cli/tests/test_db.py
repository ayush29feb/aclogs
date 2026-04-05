import json
from gym_tracker.main import app  # will be created in Task 3


def test_db_init_requires_gym_env(runner):
    from gym_tracker.db import get_db_path
    import pytest
    # Without GYM set, get_db_path raises
    import os
    old = os.environ.pop("GYM", None)
    try:
        with pytest.raises(RuntimeError, match="GYM environment variable not set"):
            get_db_path()
    finally:
        if old:
            os.environ["GYM"] = old
