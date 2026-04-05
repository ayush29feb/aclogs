# Gym — Workout Logging Tool Design

**Date:** 2026-04-05
**Status:** Approved

---

## Overview

A personal workout logging and coaching tool modeled after khana. Designed for athletic club-style workouts (block-based, supersets, conditioning + strength). The primary interaction is phone → Claude → CLI → DB, with a web dashboard for progress tracking accessible via Tailscale.

The core workflow:
1. **Pre-workout**: Upload whiteboard photo → Claude reads workout → recommends weights based on history
2. **During/after**: Log what you actually lifted (set by set or all at once)
3. **Post-workout**: Claude surfaces insights (sandbagging, flags, highlights)
4. **Pre-next-workout**: Claude pulls history for movements → recommends targets

---

## Architecture

Same split as khana:

- **`cli/`** — Python + Typer + SQLAlchemy. All writes. JSON output for Claude parsing.
- **`server/`** — Node.js + graphql-yoga + Prisma. Read-only GraphQL API.
- **`dashboard/`** — React + Relay + Vite. Mobile-first SPA, accessible via Tailscale.
- **`data/`** — SQLite DB + workout photos. Gitignored.

The coaching workflow lives in Claude, not the app. Claude calls CLI commands, confirms before writing, and interprets results.

---

## Data Model

### `exercises`
Master catalog of movements.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| name | text, unique | e.g. "Back Squat" |
| muscle_group | text | e.g. "legs", "push", "pull", "core" |
| notes | text? | form cues, coaching notes |

### `workouts`
A single training session.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| name | text | e.g. "MPA Squad W12 Upper" |
| date | date | |
| sleep_hours | float? | |
| tags | JSON array | e.g. `["squad", "upper", "w12"]` |
| notes | text? | |
| photo_path | text? | whiteboard or session photo |

### `blocks`
A superset or section within a workout (Block A, Block B, Finisher, etc.).

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| workout_id | FK → workouts | |
| name | text | e.g. "Block B — Back Squat" |
| order | int | display/execution order within workout |
| scheme | text? | e.g. "4 Sets \| RPE 8 \| Every 3:00" |

### `sets`
Atomic unit. One exercise, one round. Multiple sets with the same `round` in a block = a superset.

| Column | Type | Notes |
|--------|------|-------|
| id | PK | |
| block_id | FK → blocks | |
| exercise_id | FK → exercises | |
| round | int | groups exercises into supersets; simple sets have unique rounds |
| weight_lbs | float? | strength |
| reps | int? | strength |
| rpe | float? | 1–10 |
| duration_secs | int? | cardio |
| distance_m | float? | cardio |
| calories | float? | cardio |
| notes | text? | |
| logged_at | datetime | auto — passive rest time reference |

**Superset example** (3 rounds of curls + push-ups):
```
block: "Block B"
  round=1, exercise=curls,    reps=12, weight=30
  round=1, exercise=push-ups, reps=15
  round=2, exercise=curls,    reps=12, weight=30
  round=2, exercise=push-ups, reps=15
```

**Simple sets example** (5 sets of squats):
```
block: "Block B"
  round=1, exercise=squat, reps=5, weight=175
  round=2, exercise=squat, reps=5, weight=175
```

---

## Progress View (SQL, no extra table)

PRs and history are derived from `sets` joined across `blocks`, `workouts`, `exercises`:

```sql
SELECT w.date, s.weight_lbs, s.reps, s.rpe
FROM sets s
JOIN blocks b ON s.block_id = b.id
JOIN workouts w ON b.workout_id = w.id
JOIN exercises e ON s.exercise_id = e.id
WHERE e.name = ?
ORDER BY w.date
```

PRs: `MAX(weight_lbs) GROUP BY reps` on the above.

---

## CLI Commands

All commands output JSON. Confirmation before writes is handled by Claude, not the CLI.

### `gym exercise`
- `add --name --muscle-group [--notes]`
- `list`

### `gym workout`
- `add --name --date [--sleep] [--tags] [--notes] [--photo]`
- `show <id>` — full view: blocks → rounds → sets with exercise names
- `list [--tag] [--limit]`
- `delete <id>`

### `gym block`
- `add --workout-id --name --order [--scheme]`

### `gym set`
- `add --block-id --exercise-id --round [--weight] [--reps] [--rpe] [--duration] [--distance] [--calories] [--notes]`
- `delete <id>`

### `gym progress`
- `<exercise-name>` — full history + PRs per rep count for that exercise

---

## Dashboard

Two views, mobile-first (iPhone 14 Pro), accessible via Tailscale.

### History
- Workouts list, newest first
- Filterable by tag
- Expandable rows: blocks → rounds → sets with exercise names and numbers

### Progress
- **Big 4 spotlight**: Back Squat, Deadlift, Bench Press, Pull-ups — PR table + weight-over-time chart
- **All lifts**: same data available for any exercise
- **Cardio**: best efforts (watts, cals, distance) per machine

---

## Coaching Workflow (Claude)

Claude is the interface for the pre/post workout experience. The app provides the data layer.

**Pre-workout:**
1. User shares whiteboard photo
2. Claude reads movements, calls `gym progress <exercise>` for each key lift
3. Claude recommends targets based on history and RPE trends
4. User confirms, Claude logs the planned workout shell

**Logging:**
1. User reports sets (live or post-session)
2. Claude confirms each set, calls `gym set add`

**Post-workout insights:**
- Where weight was sandbagged vs history
- Any flags (RPE spikes, missed reps, form notes)
- Highlight (new PR, volume PR, etc.)

---

## File Structure

```
gym/
├── cli/
│   ├── gym_tracker/
│   │   ├── main.py
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── db.py
│   │   └── commands/
│   │       ├── exercise.py
│   │       ├── workout.py
│   │       ├── block.py
│   │       ├── set.py
│   │       └── progress.py
│   └── pyproject.toml
├── server/
│   ├── src/
│   │   ├── index.ts
│   │   ├── schema.ts
│   │   └── resolvers/
│   ├── prisma/schema.prisma
│   └── package.json
├── dashboard/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── RelayEnvironment.ts
│   │   └── views/
│   │       ├── HistoryView.tsx
│   │       └── ProgressView.tsx
│   └── package.json
├── data/                    # gitignored
│   ├── gym.db
│   └── images/
├── workouts/                # existing markdown logs
├── docs/
│   └── superpowers/specs/
├── .gitignore
└── setup.sh
```
