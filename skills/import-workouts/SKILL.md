---
name: import-workouts
description: Use when the user asks to import workouts, seed the database, or reload workout data
---

# Import Workouts

This wipes the existing database and re-imports all workout data from the markdown files in `workouts/`. Warn the user before proceeding.

Tell the user: "This will wipe the existing database and re-import all workouts from the source markdown files. Continue?"

Once confirmed:
```bash
source ~/.aclogs/config
cd "$ACLOGS_ROOT/cli" && uv run python import_workouts.py
```

Expected output ends with a summary of imported workouts and sessions.

If `uv` is not installed, tell the user:
> uv is required to run the import script. Install it from https://docs.astral.sh/uv/getting-started/installation/ then try again.
