#!/usr/bin/env python3
"""
Hardcoded import of historical workout data into gym.db.
Each workout is manually transcribed from the markdown files.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "gym.db"

WORKOUT_NAMES = {
    '2025-04-01': 'APS Lower — Test',
    '2025-04-02': 'APS Upper — Test',
    '2025-04-22': 'APS Upper',
    '2025-05-01': 'APS Lower',
    '2025-05-06': 'APS Upper',
    '2025-05-08': 'APS Lower',
    '2025-05-20': 'APS Upper',
    '2025-05-27': 'APS Upper',
    '2025-05-29': 'APS Lower',
    '2025-06-03': 'APS Upper',
    '2025-06-05': 'APS Lower',
    '2025-06-17': 'APS Upper',
    '2025-06-19': 'APS Lower',
    '2025-09-30': 'APS Lower — Test',
    '2025-10-21': 'APS Upper',
    '2025-10-23': 'APS Lower',
    '2026-03-05': 'MPA Lower W9',
    '2026-03-10': 'MPA Upper W10',
    '2026-03-12': 'MPA Lower W10',
    '2026-03-17': 'MPA Upper W11',
    '2026-03-19': 'MPA Lower W11',
    '2026-03-24': 'MPA Upper W12 — Deload',
    '2026-03-27': 'AC Upper W12',
    '2026-03-31': 'MPA Upper — Test',
    '2026-04-02': 'MPA Lower — Test',
}

# Each set tuple: (exercise_name, round, weight_lbs, reps, rpe, duration_secs, calories, watts, notes)

WORKOUTS = [
    # ──────────────────────────────────────────────────────────────────────────
    # 2025-04-01 — APS Lower Test (Deadlift 1RM)
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-04-01',
        'sleep_hours': None,
        'tags': ['aps', 'lower', 'test'],
        'notes': '1RM Test — Deadlift. Result: 235 lbs.',
        'blocks': [
            {
                'name': 'Deadlift — Max Test',
                'order': 1,
                'scheme': '1RM Test',
                'sets': [
                    ('Deadlift', 1, 115, 3, None, None, None, None, 'Warm-up'),
                    ('Deadlift', 2, 135, 3, None, None, None, None, 'Warm-up'),
                    ('Deadlift', 3, 155, 2, None, None, None, None, 'Build'),
                    ('Deadlift', 4, 175, 2, None, None, None, None, 'Build'),
                    ('Deadlift', 5, 195, 1, None, None, None, None, 'Heavy'),
                    ('Deadlift', 6, 205, 1, None, None, None, None, 'Heavy'),
                    ('Deadlift', 7, 225, 1, None, None, None, None, 'Near max'),
                    ('Deadlift', 8, 235, 1, None, None, None, None, 'MAX'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-04-02 — APS Upper Test (Back Squat + Bench 1RM)
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-04-02',
        'sleep_hours': None,
        'tags': ['aps', 'upper', 'test'],
        'notes': '1RM Test — Back Squat (165 lbs clean) + Bench Press (115 lbs clean).',
        'blocks': [
            {
                'name': 'Back Squat — Max Test',
                'order': 1,
                'scheme': '1RM Test',
                'sets': [
                    ('Back Squat', 1, 95, 3, None, None, None, None, 'Warm-up'),
                    ('Back Squat', 2, 115, 3, None, None, None, None, 'Warm-up'),
                    ('Back Squat', 3, 135, 2, None, None, None, None, 'Build'),
                    ('Back Squat', 4, 155, 1, None, None, None, None, 'Heavy'),
                    ('Back Squat', 5, 165, 1, None, None, None, None, 'Heavy'),
                    ('Back Squat', 6, 175, 1, None, None, None, None, 'Not low enough — depth issue'),
                    ('Back Squat', 7, 185, 1, None, None, None, None, 'Fail'),
                ],
            },
            {
                'name': 'Bench Press — Max Test',
                'order': 2,
                'scheme': '1RM Test',
                'sets': [
                    ('Bench Press', 1, 105, 5, None, None, None, None, 'Warm-up'),
                    ('Bench Press', 2, 125, 2, None, None, None, None, 'Fail'),
                    ('Bench Press', 3, 115, 1, None, None, None, None, 'Back off'),
                    ('Bench Press', 4, 125, 1, None, None, None, None, 'Ugly — grinded it'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-04-22 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-04-22',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Pendlay Row',
                'order': 1,
                'scheme': None,
                'sets': [
                    # Set 2 has "—" for reps — skipped/failed; log weight with 0 reps
                    ('Pendlay Row', 1, 75, 2, None, None, None, None, None),
                    ('Pendlay Row', 2, 85, 0, None, None, None, None, 'Failed/skipped — no reps logged'),
                ],
            },
            {
                'name': 'Lat Pulldown',
                'order': 2,
                'scheme': '3 sets',
                # "+20 lbs" = 20 lbs added weight, 3 sets — rep count not logged; use 8 as standard
                'sets': [
                    ('Lat Pulldown', 1, 20, 8, None, None, None, None, '+20 lbs, reps not logged'),
                    ('Lat Pulldown', 2, 20, 8, None, None, None, None, '+20 lbs, reps not logged'),
                    ('Lat Pulldown', 3, 20, 8, None, None, None, None, '+20 lbs, reps not logged'),
                ],
            },
            {
                'name': 'Pull Ups',
                'order': 3,
                'scheme': None,
                'sets': [
                    # Sets 1-3: 8 reps BW each
                    ('Pull-ups', 1, None, 8, None, None, None, None, 'BW'),
                    ('Pull-ups', 2, None, 8, None, None, None, None, 'BW'),
                    ('Pull-ups', 3, None, 8, None, None, None, None, 'BW'),
                    ('Pull-ups', 4, None, 5, None, None, None, None, 'BW'),
                    ('Pull-ups', 5, None, 4, None, None, None, None, 'Black band'),
                ],
            },
            {
                'name': 'Dips',
                'order': 4,
                'scheme': '4 x 6',
                'sets': [
                    ('Dips', 1, None, 6, None, None, None, None, None),
                    ('Dips', 2, None, 6, None, None, None, None, None),
                    ('Dips', 3, None, 6, None, None, None, None, None),
                    ('Dips', 4, None, 6, None, None, None, None, None),
                ],
            },
            {
                "name": "Farmer's Carry — 50m",
                'order': 5,
                'scheme': None,
                'sets': [
                    # "120 lbs x2" = 240 lbs total; "70 lbs x2" = 140 lbs total
                    ("Farmer's Carry", 1, 240, None, None, None, None, None, '120 lbs x2, 50m'),
                    ("Farmer's Carry", 2, 140, None, None, None, None, None, '70 lbs x2, 50m'),
                ],
            },
            {
                'name': 'Rowing — Intervals',
                'order': 6,
                'scheme': '1 min on / 1 min off × 8 min',
                'sets': [
                    # 4 "on" intervals at 200W, 4 "off" intervals at 120W
                    ('Row Erg', 1, None, None, None, 60, None, 200, 'On interval'),
                    ('Row Erg', 2, None, None, None, 60, None, 120, 'Off interval'),
                    ('Row Erg', 3, None, None, None, 60, None, 200, 'On interval'),
                    ('Row Erg', 4, None, None, None, 60, None, 120, 'Off interval'),
                    ('Row Erg', 5, None, None, None, 60, None, 200, 'On interval'),
                    ('Row Erg', 6, None, None, None, 60, None, 120, 'Off interval'),
                    ('Row Erg', 7, None, None, None, 60, None, 200, 'On interval'),
                    ('Row Erg', 8, None, None, None, 60, None, 120, 'Off interval'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-01 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-01',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': None,
        'blocks': [
            {
                'name': 'Warm Up — Squat',
                'order': 1,
                'scheme': None,
                'sets': [
                    # "10 x 2" = 10 reps × 2 sets
                    ('Back Squat', 1, 45, 10, None, None, None, None, 'Warm-up'),
                    ('Back Squat', 2, 45, 10, None, None, None, None, 'Warm-up'),
                ],
            },
            {
                'name': 'Primary — Back Squat',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('Back Squat', 1, 135, 8, None, None, None, None, None),
                    # Sets 2-4: 115 lbs × 8 reps × 3 sets
                    ('Back Squat', 2, 115, 8, None, None, None, None, None),
                    ('Back Squat', 3, 115, 8, None, None, None, None, None),
                    ('Back Squat', 4, 115, 8, None, None, None, None, None),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-06 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-06',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Bench Press (Eccentric Focus)',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Bench Press', 1, 75, 5, None, None, None, None, None),
                    ('Bench Press', 2, 90, 5, None, None, None, None, None),
                    ('Bench Press', 3, 95, 5, None, None, None, None, 'Hard'),
                    ('Bench Press', 4, 95, 4, None, None, None, None, 'Failed 5th'),
                    ('Bench Press', 5, 90, 5, None, None, None, None, None),
                ],
            },
            {
                'name': 'Chin Up + Plank Superset',
                'order': 2,
                'scheme': None,
                'sets': [
                    # "+15 lbs" → weight_lbs = 15 (added weight)
                    ('Chin-up', 1, 15, 3, None, None, None, None, '+15 lbs'),
                    # "+20 lbs, 3 x 3" → 3 sets of 3 reps
                    ('Chin-up', 2, 20, 3, None, None, None, None, '+20 lbs'),
                    ('Chin-up', 3, 20, 3, None, None, None, None, '+20 lbs'),
                    ('Chin-up', 4, 20, 3, None, None, None, None, '+20 lbs'),
                    ('Chin-up', 5, 35, 3, None, None, None, None, '+35 lbs'),
                    ('Chin-up', 6, 25, 1, None, None, None, None, '+25 lbs'),
                ],
            },
            {
                'name': 'Rowing',
                'order': 3,
                'scheme': None,
                'sets': [
                    ('Row Erg', 1, None, None, None, 180, None, 199, '3 min'),
                    ('Row Erg', 2, None, None, None, 120, None, 189, '2 min'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-08 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-08',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': '3s eccentric on the way down',
        'blocks': [
            {
                'name': 'Primary — Deadlift (Tempo)',
                'order': 1,
                'scheme': None,
                'sets': [
                    # Sets 1-2: 155 lbs × 5 reps × 2 sets
                    ('Deadlift', 1, 155, 5, None, None, None, None, 'Tempo'),
                    ('Deadlift', 2, 155, 5, None, None, None, None, 'Tempo'),
                    ('Deadlift', 3, 165, 5, None, None, None, None, 'Tempo'),
                    # Sets 4-5: 175 lbs × 5 reps × 2 sets
                    ('Deadlift', 4, 175, 5, None, None, None, None, 'Tempo'),
                    ('Deadlift', 5, 175, 5, None, None, None, None, 'Tempo'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-20 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-20',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': '1RM was 125 lbs — hit 145 lbs easily this session (PR!)',
        'blocks': [
            {
                'name': 'Primary — Bench Press',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Bench Press', 1, 85, 5, None, None, None, None, None),
                    ('Bench Press', 2, 95, 5, None, None, None, None, None),
                    ('Bench Press', 3, 105, 5, None, None, None, None, None),
                    ('Bench Press', 4, 110, 5, None, None, None, None, None),
                    ('Bench Press', 5, 115, 5, None, None, None, None, None),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-27 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-27',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Pull Ups (weighted)',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Pull-ups', 1, None, 5, None, None, None, None, 'BW'),
                    ('Pull-ups', 2, 10, 5, None, None, None, None, '+10 lbs'),
                    ('Pull-ups', 3, 35, 3, None, None, None, None, '+35 lbs'),
                    ('Pull-ups', 4, 30, 3, None, None, None, None, '+30 lbs'),
                    ('Pull-ups', 5, 25, 2, None, None, None, None, '+25 lbs'),
                    ('Pull-ups', 6, None, 3, None, None, None, None, 'BW'),
                ],
            },
            {
                'name': 'DB Chest Press',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('DB Floor Press', 1, 40, 8, None, None, None, None, None),
                    ('DB Floor Press', 2, 45, 8, None, None, None, None, None),
                    ('DB Floor Press', 3, 40, 6, None, None, None, None, None),
                ],
            },
            {
                'name': 'Sit Ups (weighted)',
                'order': 3,
                'scheme': None,
                'sets': [
                    ('Sit-up', 1, 25, 12, None, None, None, None, None),
                    ('Sit-up', 2, 35, 6, None, None, None, None, None),
                    ('Sit-up', 3, 25, 6, None, None, None, None, None),
                    ('Sit-up', 4, 25, 6, None, None, None, None, None),
                ],
            },
            {
                'name': 'Bent Over Supinated to Pronated Row',
                'order': 4,
                # "3 x 10/10" = 3 sets of 10 reps each side = 20 total reps per set; log as 20 reps
                'scheme': '3 x 10/10',
                'sets': [
                    ('Bent Over Row', 1, 20, 20, None, None, None, None, '10/10 each side'),
                    ('Bent Over Row', 2, 20, 20, None, None, None, None, '10/10 each side'),
                    ('Bent Over Row', 3, 20, 20, None, None, None, None, '10/10 each side'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-05-29 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-05-29',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': None,
        'blocks': [
            {
                'name': 'Primary — Back Squat',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Back Squat', 1, 105, 5, None, None, None, None, None),
                    ('Back Squat', 2, 115, 5, None, None, None, None, None),
                    ('Back Squat', 3, 125, 3, None, None, None, None, None),
                    ('Back Squat', 4, 135, 3, None, None, None, None, None),
                    ('Back Squat', 5, 145, 3, None, None, None, None, None),
                ],
            },
            {
                'name': 'Glute Bridge',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('Glute Bridge', 1, 165, 6, None, None, None, None, None),
                    ('Glute Bridge', 2, 175, 6, None, None, None, None, None),
                    ('Glute Bridge', 3, 175, 6, None, None, None, None, None),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-06-03 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-06-03',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Primary — Bench Press',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Bench Press', 1, 100, 5, None, None, None, None, None),
                    ('Bench Press', 2, 105, 5, None, None, None, None, None),
                    ('Bench Press', 3, 115, 3, None, None, None, None, None),
                    ('Bench Press', 4, 120, 3, None, None, None, None, None),
                    ('Bench Press', 5, 125, 1, None, None, None, None, None),
                    ('Bench Press', 6, 120, 2, None, None, None, None, None),
                ],
            },
            {
                'name': 'Pendlay Row',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('Pendlay Row', 1, 95, 6, None, None, None, None, None),
                    ('Pendlay Row', 2, 105, 6, None, None, None, None, None),
                    ('Pendlay Row', 3, 115, 6, None, None, None, None, None),
                    ('Pendlay Row', 4, 115, 6, None, None, None, None, None),
                ],
            },
            {
                'name': 'Finisher',
                'order': 3,
                'scheme': None,
                'sets': [
                    # Plate Pass: 4 x 12 reps at 15 lbs
                    ('Plate Pass', 1, 15, 12, None, None, None, None, None),
                    ('Plate Pass', 2, 15, 12, None, None, None, None, None),
                    ('Plate Pass', 3, 15, 12, None, None, None, None, None),
                    ('Plate Pass', 4, 15, 12, None, None, None, None, None),
                    # Rowing: 5 min at 200W
                    ('Row Erg', 1, None, None, None, 300, None, 200, '5 min'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-06-05 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-06-05',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': None,
        'blocks': [
            {
                'name': 'Primary — Deadlift',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Deadlift', 1, 175, 5, None, None, None, None, None),
                    ('Deadlift', 2, 205, 5, None, None, None, None, None),
                    ('Deadlift', 3, 225, 3, None, None, None, None, None),
                    ('Deadlift', 4, 245, 3, None, None, None, None, 'Slow'),
                    ('Deadlift', 5, 225, 3, None, None, None, None, 'Back off'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-06-17 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-06-17',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Primary — Bench Press',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Bench Press', 1, 105, 3, None, None, None, None, None),
                    ('Bench Press', 2, 125, 3, None, None, None, None, None),
                    ('Bench Press', 3, 125, 2, None, None, None, None, None),
                    ('Bench Press', 4, 135, 2, None, None, None, None, None),
                    ('Bench Press', 5, 135, 2, None, None, None, None, None),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-06-19 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-06-19',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': None,
        'blocks': [
            {
                'name': 'Deadlift — Speed',
                'order': 1,
                'scheme': None,
                'sets': [
                    ('Deadlift', 1, 135, 3, None, None, None, None, 'Fast'),
                ],
            },
            {
                'name': 'Deadlift — Working Sets',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('Deadlift', 1, 185, 3, None, None, None, None, None),
                    ('Deadlift', 2, 205, 3, None, None, None, None, None),
                    ('Deadlift', 3, 225, 2, None, None, None, None, None),
                    ('Deadlift', 4, 235, 2, None, None, None, None, None),
                    ('Deadlift', 5, 245, 2, None, None, None, None, None),
                ],
            },
            {
                'name': 'Bulgarian Split Squat',
                'order': 3,
                'scheme': None,
                'sets': [
                    # "5/5" = 5 reps each leg = 10 total; "4/4" = 8 total
                    ('Bulgarian Split Squat', 1, 60, 10, None, None, None, None, '5/5 each leg'),
                    ('Bulgarian Split Squat', 2, 60, 8, None, None, None, None, '4/4 each leg'),
                    ('Bulgarian Split Squat', 3, 60, 8, None, None, None, None, '4/4 each leg'),
                    ('Bulgarian Split Squat', 4, 60, 8, None, None, None, None, '4/4 each leg'),
                ],
            },
            {
                'name': 'Plank (weighted)',
                'order': 4,
                'scheme': None,
                'sets': [
                    ('Plank', 1, 55, None, None, 45, None, None, '45s'),
                    ('Plank', 2, 55, None, None, 45, None, None, '45s'),
                    ('Plank', 3, 45, None, None, 45, None, None, '45s'),
                    ('Plank', 4, 45, None, None, 45, None, None, '45s'),
                ],
            },
            {
                'name': 'Cyclist Squat + Row',
                'order': 5,
                'scheme': None,
                'sets': [
                    # Cyclist Squat: 4 x 10 @ 25 lbs
                    ('Cyclist Squat', 1, 25, 10, None, None, None, None, None),
                    ('Cyclist Squat', 2, 25, 10, None, None, None, None, None),
                    ('Cyclist Squat', 3, 25, 10, None, None, None, None, None),
                    ('Cyclist Squat', 4, 25, 10, None, None, None, None, None),
                    # Row: 4 × 150m distance rows (no reps, distance-based)
                    ('Row Erg', 1, None, None, None, None, None, None, '150m'),
                    ('Row Erg', 2, None, None, None, None, None, None, '150m'),
                    ('Row Erg', 3, None, None, None, None, None, None, '150m'),
                    ('Row Erg', 4, None, None, None, None, None, None, '150m'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-09-30 — APS Lower Test (Deadlift 1RM)
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-09-30',
        'sleep_hours': None,
        'tags': ['aps', 'lower', 'test'],
        'notes': '1RM Test — Deadlift. Target 260 lbs. Result: 260 lbs ✅',
        'blocks': [
            {
                'name': 'Deadlift — Max Test',
                'order': 1,
                'scheme': '1RM Test',
                'sets': [
                    ('Deadlift', 1, 145, 3, None, None, None, None, 'Warm-up, 55%'),
                    ('Deadlift', 2, 175, 3, None, None, None, None, 'Warm-up, 65%'),
                    ('Deadlift', 3, 205, 2, None, None, None, None, 'Build, 75%'),
                    ('Deadlift', 4, 225, 2, None, None, None, None, 'Build, 83%'),
                    ('Deadlift', 5, 235, 1, None, None, None, None, 'Heavy, 88%'),
                    ('Deadlift', 6, 245, 1, None, None, None, None, 'Heavy, 93%'),
                    ('Deadlift', 7, 255, 1, None, None, None, None, 'Near max, 97%'),
                    ('Deadlift', 8, 260, 1, None, None, None, None, 'MAX — hit target'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-10-21 — APS Upper
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-10-21',
        'sleep_hours': None,
        'tags': ['aps', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Warm Up',
                'order': 1,
                'scheme': None,
                'sets': [
                    # Bench empty bar: "—" weight → null weight, 16 reps
                    ('Bench Press', 1, None, 16, None, None, None, None, 'Empty bar warm-up'),
                    # Gorilla Rows: 26 lbs x2 = 52 lbs total, 16 reps
                    ('Gorilla Row', 1, 52, 16, None, None, None, None, '26 lbs x2'),
                    # Push Press: 15 lbs, 12 reps
                    ('Push Press', 1, 15, 12, None, None, None, None, None),
                ],
            },
            {
                'name': 'Prime',
                'order': 2,
                'scheme': None,
                'sets': [
                    # Bench w/ Legs Raised: 3 x 8 @ 60 lbs (normalize to Bench Press)
                    ('Bench Press', 1, 60, 8, None, None, None, None, 'Legs raised'),
                    ('Bench Press', 2, 60, 8, None, None, None, None, 'Legs raised'),
                    ('Bench Press', 3, 60, 8, None, None, None, None, 'Legs raised'),
                    # DB Pullover: "x 8-10" → 9 reps @ 30 lbs
                    ('DB Pullover', 1, 30, 9, None, None, None, None, '8-10 reps'),
                ],
            },
            {
                'name': 'Primary — Bench Press',
                'order': 3,
                'scheme': None,
                'sets': [
                    ('Bench Press', 1, 75, 10, None, None, None, None, None),
                    ('Bench Press', 2, 85, 8, None, None, None, None, None),
                    ('Bench Press', 3, 75, 8, None, None, None, None, None),
                    ('Bench Press', 4, 75, 9, None, None, None, None, None),
                ],
            },
            {
                'name': 'Secondary',
                'order': 4,
                'scheme': None,
                'sets': [
                    # Reverse Row: 4 x 10
                    ('Reverse Row', 1, None, 10, None, None, None, None, None),
                    ('Reverse Row', 2, None, 10, None, None, None, None, None),
                    ('Reverse Row', 3, None, 10, None, None, None, None, None),
                    ('Reverse Row', 4, None, 10, None, None, None, None, None),
                    # Push Up: "10 reps" — 1 set
                    ('Push-up', 1, None, 10, None, None, None, None, None),
                    # Knee Push Up: 3 x 10
                    ('Push-up', 2, None, 10, None, None, None, None, 'Knee push-up'),
                    ('Push-up', 3, None, 10, None, None, None, None, 'Knee push-up'),
                    ('Push-up', 4, None, 10, None, None, None, None, 'Knee push-up'),
                ],
            },
            {
                'name': 'Finisher',
                'order': 5,
                'scheme': None,
                'sets': [
                    # Arnold Press (21s): 12 lbs x2 = 24 lbs, then 10 lbs x2 = 20 lbs; "—" reps = 21s protocol
                    ('Arnold Press', 1, 24, 21, None, None, None, None, '21s protocol, 12 lbs x2'),
                    ('Arnold Press', 2, 20, 21, None, None, None, None, '21s protocol, 10 lbs x2'),
                    # Pull Through: 3 x 10 @ 25 lbs
                    ('Pull Through', 1, 25, 10, None, None, None, None, None),
                    ('Pull Through', 2, 25, 10, None, None, None, None, None),
                    ('Pull Through', 3, 25, 10, None, None, None, None, None),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2025-10-23 — APS Lower
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2025-10-23',
        'sleep_hours': None,
        'tags': ['aps', 'lower'],
        'notes': 'Strength + Conditioning',
        'blocks': [
            {
                'name': 'Prime',
                'order': 1,
                'scheme': None,
                'sets': [
                    # Banded Deadlift: 3 x 5 @ 105 lbs
                    ('Banded Deadlift', 1, 105, 5, None, None, None, None, None),
                    ('Banded Deadlift', 2, 105, 5, None, None, None, None, None),
                    ('Banded Deadlift', 3, 105, 5, None, None, None, None, None),
                    # Reverse Leg Raises: 3 x 6-8 @ BW
                    ('Reverse Leg Raise', 1, None, 7, None, None, None, None, '6-8 reps'),
                    ('Reverse Leg Raise', 2, None, 7, None, None, None, None, '6-8 reps'),
                    ('Reverse Leg Raise', 3, None, 7, None, None, None, None, '6-8 reps'),
                ],
            },
            {
                'name': 'Primary — Deadlift',
                'order': 2,
                'scheme': None,
                'sets': [
                    ('Deadlift', 1, 135, 5, None, None, None, None, None),
                    ('Deadlift', 2, 155, 6, None, None, None, None, None),
                    ('Deadlift', 3, 160, 6, None, None, None, None, None),
                    ('Deadlift', 4, 175, 6, None, None, None, None, None),
                ],
            },
            {
                'name': 'Secondary',
                'order': 3,
                'scheme': None,
                'sets': [
                    # Front Rack Squat: 3 x 8 @ 165 lbs
                    ('Front Rack Squat', 1, 165, 8, None, None, None, None, None),
                    ('Front Rack Squat', 2, 165, 8, None, None, None, None, None),
                    ('Front Rack Squat', 3, 165, 8, None, None, None, None, None),
                    # Deficit Reverse Lunge: 2 x 6,6 @ 30 lbs = 12 reps per set
                    ('Reverse Lunge', 1, 30, 6, None, None, None, None, 'Deficit'),
                    ('Reverse Lunge', 2, 30, 6, None, None, None, None, 'Deficit'),
                ],
            },
            {
                'name': 'Rowing Conditioning',
                'order': 4,
                'scheme': '3 rounds: 1 min on / 1 min off',
                'sets': [
                    # 3 rounds: 1 min on at 200W, 1 min off at ~120/115/105W
                    ('Row Erg', 1, None, None, None, 60, None, 200, 'Round 1 — On'),
                    ('Row Erg', 2, None, None, None, 60, None, 120, 'Round 1 — Off'),
                    ('Row Erg', 3, None, None, None, 60, None, 200, 'Round 2 — On'),
                    ('Row Erg', 4, None, None, None, 60, None, 115, 'Round 2 — Off'),
                    ('Row Erg', 5, None, None, None, 60, None, 200, 'Round 3 — On'),
                    ('Row Erg', 6, None, None, None, 60, None, 105, 'Round 3 — Off'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-05 — MPA Lower W9
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-05',
        'sleep_hours': 1.5,
        'tags': ['mpa', 'squad', 'lower'],
        'notes': 'Hamstrings felt weird early, lower back flagged on RDL set 3 — pulled back smartly',
        'blocks': [
            {
                'name': 'Block A — MetCon (partial)',
                'order': 1,
                'scheme': 'Pyramid format — did opening + closing',
                'sets': [
                    # Burpee to plate: 20 reps
                    ('Burpee', 1, None, 20, None, None, None, None, 'Burpee to plate'),
                    # Row: 30 cal / 2 min
                    ('Row Erg', 1, None, None, None, 120, None, None, '30 cal / 2 min'),
                    # Front rack squat: 20 reps @ 20 lbs
                    ('Front Rack Squat', 1, 20, 20, None, None, None, None, None),
                    # Row: 15 cal / 1 min
                    ('Row Erg', 2, None, None, None, 60, None, None, '15 cal / 1 min'),
                    # Burpees: 10
                    ('Burpee', 2, None, 10, None, None, None, None, None),
                ],
            },
            {
                'name': 'Block B — BB Back Squat',
                'order': 2,
                'scheme': '6 sets: 6,5,5,3,3,3 @ RPE 8 + 20s hollow hold between sets',
                'sets': [
                    ('Back Squat', 1, 95, 6, 8, None, None, None, 'Warm-up feel'),
                    ('Back Squat', 2, 105, 5, 8, None, None, None, None),
                    ('Back Squat', 3, 115, 5, 8, None, None, None, None),
                    ('Back Squat', 4, 135, 3, 8, None, None, None, 'Stayed here'),
                    ('Back Squat', 5, 135, 3, 8, None, None, None, None),
                    ('Back Squat', 6, 135, 3, 8, None, None, None, None),
                ],
            },
            {
                'name': 'Block C — KB Cross Body RDL + Bulgarian Split Squat',
                'order': 3,
                'scheme': '4 sets @ RPE 8',
                'sets': [
                    # RDL set 1: 35 lbs (yellow KB) — 5 reps each (standard accessory scheme)
                    ('KB RDL', 1, 35, 5, 8, None, None, None, 'Yellow KB'),
                    ('Bulgarian Split Squat', 1, 20, 5, 8, None, None, None, '20 lbs DBs'),
                    # RDL set 2: 44 lbs (gray KB)
                    ('KB RDL', 2, 44, 5, 8, None, None, None, 'Gray KB'),
                    ('Bulgarian Split Squat', 2, 20, 5, 8, None, None, None, '20 lbs DBs'),
                    # RDL set 3: 44 lbs, lower back flagged — partial set, log as stopped
                    ('KB RDL', 3, 44, 5, 8, None, None, None, 'Lower back flagged — stopped'),
                    ('Bulgarian Split Squat', 3, 20, 5, 8, None, None, None, '20 lbs DBs'),
                    # RDL set 4: skipped; split squat only
                    ('Bulgarian Split Squat', 4, 20, 5, 8, None, None, None, 'RDL skipped, split squat only'),
                ],
            },
            {
                'name': 'Finisher — Core EMOM x2 rounds',
                'order': 4,
                'scheme': 'EMOM x2',
                'sets': [
                    ('Sit-up', 1, None, 15, None, None, None, None, 'Atomic sit-up, ~15 reps'),
                    ('KB Toe Touch', 1, None, 8, None, None, None, None, '~8 reps'),
                    ('Sit-up', 2, None, 8, None, None, None, None, 'Atomic sit-up, ~half + breaks'),
                    ('KB Toe Touch', 2, None, 4, None, None, None, None, '~half + breaks'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-10 — MPA Upper W10
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-10',
        'sleep_hours': 3.0,
        'tags': ['mpa', 'squad', 'upper'],
        'notes': '~3 hrs sleep — still hit a row PR (135 lbs).',
        'blocks': [
            {
                'name': 'Block A — Conditioning',
                'order': 1,
                # E4MOM × 3: Ski/KB Swing/Echo Bike — 2 rounds logged
                'scheme': 'E4MOM × 3 (In Pairs) — Scaled',
                'sets': [
                    # Round 1
                    ('Ski Erg', 1, None, None, None, None, 20, None, '2×10 (20 cal)'),
                    ('KB Swing', 1, None, 15, None, None, None, None, 'Yellow DBs'),
                    ('Echo Bike', 1, None, None, None, None, 10, None, '10 cal'),
                    # Round 2
                    ('Ski Erg', 2, None, None, None, None, 20, None, '2×10 (20 cal)'),
                    ('KB Swing', 2, None, 15, None, None, None, None, 'Yellow DBs'),
                    ('Echo Bike', 2, None, None, None, None, 10, None, '10 cal (ski)'),
                    # Burpees at end
                    ('Burpee', 1, None, 7, None, None, None, None, '5 + 2 = 7 total'),
                ],
            },
            {
                'name': 'Block B — Strength + Power',
                'order': 2,
                # Bent Over Row scheme: 5,5,3,3,3; Incline Plyo Push Up: 5 all sets
                'scheme': '5 Sets | RPE 8 | Every 2:30',
                'sets': [
                    ('Bent Over Row', 1, 95, 5, 8, None, None, None, None),
                    ('Push-up', 1, None, 5, None, None, None, None, 'Incline Plyo Push Up w/Reset'),
                    ('Bent Over Row', 2, 105, 5, 8, None, None, None, None),
                    ('Push-up', 2, None, 5, None, None, None, None, 'Incline Plyo Push Up w/Reset'),
                    ('Bent Over Row', 3, 125, 3, 8, None, None, None, None),
                    ('Push-up', 3, None, 5, None, None, None, None, 'Incline Plyo Push Up w/Reset'),
                    ('Bent Over Row', 4, 125, 3, 8, None, None, None, None),
                    ('Push-up', 4, None, 5, None, None, None, None, 'Incline Plyo Push Up w/Reset'),
                    ('Bent Over Row', 5, 135, 3, 8, None, None, None, 'PR'),
                    ('Push-up', 5, None, 5, None, None, None, None, 'Incline Plyo Push Up w/Reset'),
                ],
            },
            {
                'name': 'Block C — Strength + Power',
                'order': 3,
                # Push Up: 8-12/6-10 reps; KB Pendlay Row: 6 reps all sets
                # "2 × 44" = 88 lbs total for KB Pendlay Row
                'scheme': '5 Sets | RPE 8 | Every 2:00',
                'sets': [
                    # Set 1: Push Up 5+3 broken = 8 total; KB Pendlay Row 2×44=88 lbs, 6 reps
                    ('Push-up', 1, None, 8, 7, None, None, None, '5+3 broken'),
                    ('KB Pendlay Row', 1, 88, 6, 7, None, None, None, '2×44 lbs'),
                    # Set 2
                    ('Push-up', 2, None, 8, 8, None, None, None, None),
                    ('KB Pendlay Row', 2, 88, 6, 8, None, None, None, '2×44 lbs'),
                    # Set 3
                    ('Push-up', 3, None, 5, 8, None, None, None, None),
                    ('KB Pendlay Row', 3, 88, 6, 8, None, None, None, '2×44 lbs'),
                    # Set 4
                    ('Push-up', 4, None, 5, 8, None, None, None, None),
                    ('KB Pendlay Row', 4, 88, 6, 8, None, None, None, '2×44 lbs'),
                    # Set 5
                    ('Push-up', 5, None, 4, 8, None, None, None, None),
                    ('KB Pendlay Row', 5, 88, 6, 8, None, None, None, '2×44 lbs'),
                    # Set 6: Push up only (no row)
                    ('Push-up', 6, None, 5, None, None, None, None, None),
                ],
            },
            {
                'name': 'Finisher — MetCon',
                'order': 4,
                'scheme': '21-15-9 | 4:00 Cap',
                'sets': [
                    # Plate G2OH: 21-15-9 = 45 total reps; log as 3 sets
                    ('Plate G2OH', 1, 15, 21, None, None, None, None, 'Round of 21'),
                    ('Russian Twist', 1, 15, 21, None, None, None, None, 'Round of 21'),
                    ('Plate G2OH', 2, 15, 15, None, None, None, None, 'Round of 15'),
                    ('Russian Twist', 2, 15, 15, None, None, None, None, 'Round of 15'),
                    ('Plate G2OH', 3, 15, 9, None, None, None, None, 'Round of 9'),
                    ('Russian Twist', 3, 15, 9, None, None, None, None, 'Round of 9'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-12 — MPA Lower W10
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-12',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'lower'],
        'notes': None,
        'blocks': [
            {
                'name': 'Block A — Conditioning',
                'order': 1,
                'scheme': 'E4MOM × 3 (In Pairs) — Scaled',
                'sets': [
                    # C2 Bike: 80 cal total over 2 rounds
                    ('Echo Bike', 1, None, None, None, None, 40, 168, 'Round 1, ~40 cal'),
                    # Goblet Squat: 15 reps @ 25 lbs
                    ('Goblet Squat', 1, 25, 15, None, None, None, None, None),
                    # Round 2
                    ('Echo Bike', 2, None, None, None, None, 41, 168, 'Round 2, ~41 cal'),
                    ('Goblet Squat', 2, 25, 15, None, None, None, None, None),
                ],
            },
            {
                'name': 'Block B — Strength + Power',
                'order': 2,
                # Deadlift scheme: 5,5,3,3,3; Box Jump: 5 all sets
                # Note: set 5 has ×1 reps (not matching scheme) — use what's logged
                'scheme': '5 Sets | RPE 8 | Every 2:30',
                'sets': [
                    ('Deadlift', 1, 165, 5, 6, None, None, None, None),
                    ('Box Jump', 1, None, 5, 6, None, None, None, 'Hurdle to Box Jump'),
                    ('Deadlift', 2, 185, 5, 7, None, None, None, None),
                    ('Box Jump', 2, None, 5, 7, None, None, None, 'Hurdle to Box Jump'),
                    ('Deadlift', 3, 205, 3, 8, None, None, None, None),
                    ('Box Jump', 3, None, 5, 8, None, None, None, 'Hurdle to Box Jump'),
                    ('Deadlift', 4, 225, 3, 8, None, None, None, None),
                    ('Box Jump', 4, None, 5, 8, None, None, None, 'Hurdle to Box Jump'),
                    # Set 5: ×1 as logged
                    ('Deadlift', 5, 245, 1, 8, None, None, None, None),
                    ('Box Jump', 5, None, 5, 8, None, None, None, 'Hurdle to Box Jump'),
                ],
            },
            {
                'name': 'Block C — Strength',
                'order': 3,
                # KB Step Up scheme: 6,6; Reverse Lunge: 10 all sets
                # "2 × 26" = 52 lbs for step ups; "2 × 18" = 36 lbs
                'scheme': '4 Sets | RPE 8 | Every 3:00',
                'sets': [
                    ('Step-up', 1, 52, 6, None, None, None, None, '2×26 lbs, RPE 6-7'),
                    ('Reverse Lunge', 1, 35, 10, None, None, None, None, None),
                    ('Step-up', 2, 52, 6, None, None, None, None, '2×26 lbs'),
                    ('Reverse Lunge', 2, 35, 10, None, None, None, None, None),
                    ('Step-up', 3, 36, 6, None, None, None, None, '2×18 lbs, dropped weight'),
                    ('Reverse Lunge', 3, 30, 10, None, None, None, None, None),
                    ('Step-up', 4, 36, 6, None, None, None, None, '2×18 lbs'),
                    ('Reverse Lunge', 4, 30, 10, None, None, None, None, None),
                    # Set 5: lunges only, ran out of time
                    ('Reverse Lunge', 5, 30, 10, None, None, None, None, 'Lunges only, ran out of time'),
                ],
            },
            {
                'name': 'Finisher — MetCon',
                'order': 4,
                'scheme': '21-15-9 | 4:00 Cap',
                'sets': [
                    # B/R Forward Lunge + Butterfly Sit Up: 21 + 15 (hit cap before 9s)
                    ('Reverse Lunge', 1, None, 21, None, None, None, None, 'B/R Forward Lunge, round of 21'),
                    ('Sit-up', 1, None, 21, None, None, None, None, 'Butterfly, round of 21'),
                    ('Reverse Lunge', 2, None, 15, None, None, None, None, 'B/R Forward Lunge, round of 15'),
                    ('Sit-up', 2, None, 15, None, None, None, None, 'Butterfly, round of 15 — hit cap'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-17 — MPA Upper W11
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-17',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'upper'],
        'notes': None,
        'blocks': [
            {
                'name': 'Block A — IWT (E4MOM × 12)',
                'order': 1,
                # 3 rounds (E4MOM×12 = 12/4 = 3 rounds)
                'scheme': 'E4MOM × 12, 3 rounds',
                'sets': [
                    # Round 1
                    ('DB Floor Press', 1, 25, 12, None, None, None, None, 'DB Bridged Floor Press'),
                    ('Ski Erg', 1, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('DB High Pull', 1, 15, 12, None, None, None, None, None),
                    ('Echo Bike', 1, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    # Round 2
                    ('DB Floor Press', 2, 25, 12, None, None, None, None, 'DB Bridged Floor Press'),
                    ('Ski Erg', 2, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('DB High Pull', 2, 15, 12, None, None, None, None, None),
                    ('Echo Bike', 2, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    # Round 3
                    ('DB Floor Press', 3, 25, 12, None, None, None, None, 'DB Bridged Floor Press'),
                    ('Ski Erg', 3, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('DB High Pull', 3, 15, 12, None, None, None, None, None),
                    ('Echo Bike', 3, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                ],
            },
            {
                'name': 'Block B — Strength',
                'order': 2,
                # Bench Press scheme: 5,5,5,3,3,3; KB Pendlay Row: 5 all sets
                # "2 × 26" = 52 lbs for KB Pendlay Row
                'scheme': '6 Sets | RPE 8 | Every 2:00',
                'sets': [
                    ('Bench Press', 1, 85, 5, 6.5, None, None, None, 'RPE 6-7'),
                    ('KB Pendlay Row', 1, 52, 5, 6.5, None, None, None, '2×26 lbs, RPE 6-7'),
                    ('Bench Press', 2, 95, 5, 8, None, None, None, None),
                    ('KB Pendlay Row', 2, 52, 5, 8, None, None, None, '2×26 lbs'),
                    ('Bench Press', 3, 95, 5, 8, None, None, None, None),
                    ('KB Pendlay Row', 3, 52, 5, 8, None, None, None, '2×26 lbs'),
                    ('Bench Press', 4, 105, 3, 8, None, None, None, None),
                    ('KB Pendlay Row', 4, 52, 5, 8, None, None, None, '2×26 lbs'),
                    ('Bench Press', 5, 100, 3, 8, None, None, None, None),
                    ('KB Pendlay Row', 5, 52, 5, 8, None, None, None, '2×26 lbs'),
                    ('Bench Press', 6, 100, 3, 8, None, None, None, None),
                    ('KB Pendlay Row', 6, 52, 5, 8, None, None, None, '2×26 lbs'),
                ],
            },
            {
                'name': 'Block C — Strength',
                'order': 3,
                # Box Plank KB Row scheme: 6,6; DB Shoulder Press: 8,8
                # 16kg = 35.3 lbs; 20kg = 44.1 lbs
                'scheme': '5 Sets | RPE 8 | Every 2:30',
                'sets': [
                    ('KB Plank Row', 1, 35.3, 6, 7, None, None, None, '16kg, RPE 7'),
                    ('DB Shoulder Press', 1, 25, 8, 7, None, None, None, None),
                    ('KB Plank Row', 2, 35.3, 6, 8, None, None, None, '16kg'),
                    ('DB Shoulder Press', 2, 25, 8, 8, None, None, None, None),
                    ('KB Plank Row', 3, 35.3, 6, 8, None, None, None, '16kg'),
                    ('DB Shoulder Press', 3, 20, 8, 8, None, None, None, None),
                    ('KB Plank Row', 4, 35.3, 6, 8, None, None, None, '16kg'),
                    ('DB Shoulder Press', 4, 20, 8, 8, None, None, None, None),
                    # Set 5: 20kg = 44.1 lbs for KB Row; 25 lbs DB press (struggled)
                    ('KB Plank Row', 5, 44.1, 6, 8, None, None, None, '20kg'),
                    ('DB Shoulder Press', 5, 25, 8, 8, None, None, None, 'Struggled on press'),
                ],
            },
            {
                'name': 'Finisher — EMOM × 4',
                'order': 4,
                'scheme': 'EMOM × 4',
                'sets': [
                    ('Plank', 1, None, None, None, 30, None, None, 'Tall plank, 30 secs'),
                    ('Push-up', 1, None, None, None, 20, None, None, 'Bottom of push-up hold, 20 secs'),
                    ('Plank', 2, None, None, None, 30, None, None, 'Tall plank, 30 secs'),
                    ('Push-up', 2, None, None, None, 20, None, None, 'Bottom of push-up hold, 20 secs'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-19 — MPA Lower W11
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-19',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'lower'],
        'notes': 'Makeup class — 8:28 PM',
        'blocks': [
            {
                'name': 'Block A — Strength + Power',
                'order': 1,
                # Split Squat scheme: 5,5; KB Swing: 5 all sets
                # 16kg = 35.3 lbs; ~20kg = 44.1 lbs
                'scheme': '4 Sets | RPE 8 | Every 3:00',
                'sets': [
                    ('Bulgarian Split Squat', 1, 35.3, 5, 8, None, None, None, '16kg yellow'),
                    ('KB Swing', 1, 35.3, 5, 8, None, None, None, '16kg blue'),
                    ('Bulgarian Split Squat', 2, 35.3, 5, 8, None, None, None, '16kg yellow'),
                    ('KB Swing', 2, 35.3, 5, 8, None, None, None, '16kg blue'),
                    ('Bulgarian Split Squat', 3, 44.1, 5, 8, None, None, None, '~20kg, weight unsure'),
                    ('KB Swing', 3, 35.3, 5, 8, None, None, None, '16kg blue'),
                    ('Bulgarian Split Squat', 4, 44.1, 5, 8, None, None, None, '~20kg'),
                    ('KB Swing', 4, 35.3, 5, 8, None, None, None, '16kg yellow, last set'),
                ],
            },
            {
                'name': 'Block B — Strength + Power',
                'order': 2,
                # Back Squat scheme: 5,5,3,3,3; Box Jump: 5 all sets
                'scheme': '5 Sets | RPE 9 | Every 2:30',
                'sets': [
                    ('Back Squat', 1, 95, 5, 6, None, None, None, 'RPE 6'),
                    ('Box Jump', 1, None, 5, 6, None, None, None, 'Seated Box Jump'),
                    ('Back Squat', 2, 125, 5, 7, None, None, None, 'RPE 7'),
                    ('Box Jump', 2, None, 5, 7, None, None, None, 'Seated Box Jump'),
                    ('Back Squat', 3, 135, 3, 9, None, None, None, 'RPE 9'),
                    ('Box Jump', 3, None, 5, 9, None, None, None, 'Seated Box Jump'),
                    ('Back Squat', 4, 135, 3, 9, None, None, None, 'RPE 9'),
                    ('Box Jump', 4, None, 5, 9, None, None, None, 'Seated Box Jump'),
                    ('Back Squat', 5, 135, 3, 9, None, None, None, 'RPE 9'),
                    ('Box Jump', 5, None, 5, 9, None, None, None, 'Seated Box Jump'),
                ],
            },
            {
                'name': 'Block C — IWT (EMOM × 12)',
                'order': 3,
                # 3 rounds (EMOM×12 / 4 min = 3 rounds)
                'scheme': 'EMOM × 12, 3 rounds',
                'sets': [
                    # Round 1
                    ('DB RDL', 1, 35, 12, None, None, None, None, 'Heavy DB RDL'),
                    ('Echo Bike', 1, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('Goblet Squat', 1, 30, 12, None, None, None, None, 'Deadball Squat'),
                    ('Row Erg', 1, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    # Round 2
                    ('DB RDL', 2, 35, 12, None, None, None, None, 'Heavy DB RDL'),
                    ('Echo Bike', 2, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('Goblet Squat', 2, 30, 12, None, None, None, None, 'Deadball Squat'),
                    ('Row Erg', 2, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    # Round 3
                    ('DB RDL', 3, 35, 12, None, None, None, None, 'Heavy DB RDL'),
                    ('Echo Bike', 3, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                    ('Goblet Squat', 3, 30, 12, None, None, None, None, 'Deadball Squat'),
                    ('Row Erg', 3, None, None, None, 20, None, None, '20 secs @ RPE 10'),
                ],
            },
            {
                'name': 'Finisher — EMOM × 4',
                'order': 4,
                'scheme': 'EMOM × 4',
                'sets': [
                    ('Goblet Squat', 1, None, None, None, 30, None, None, 'Goblet bottom of squat hold, 30 secs'),
                    ('Reverse Lunge', 1, None, None, None, 30, None, None, 'Goblet reverse lunge, 30 secs'),
                    ('Goblet Squat', 2, None, None, None, 30, None, None, 'Goblet bottom of squat hold, 30 secs'),
                    ('Reverse Lunge', 2, None, None, None, 30, None, None, 'Goblet reverse lunge, 30 secs'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-24 — MPA Upper W12 Deload
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-24',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'upper', 'deload'],
        'notes': 'Deload week — lower RPE than usual (7-8 vs 8-9)',
        'blocks': [
            {
                'name': 'Block A — Conditioning',
                'order': 1,
                'scheme': 'E6MOM × 2 (In Pairs)',
                'sets': [
                    # Round A
                    ('Echo Bike', 1, None, None, None, None, 15, 250, 'Round A — 15 cal @~250W'),
                    ('DB Snatch', 1, 35, 16, None, None, None, None, 'Round A — 16 reps @ 30-40 lbs'),
                    ('DB Burpee Deadlift', 1, 35, 15, None, None, None, None, 'Round A — 15 reps @ 30-40 lbs'),
                    # Round B
                    ('DB Snatch', 2, 35, 15, None, None, None, None, 'Round B — 15 reps @ 30-40 lbs'),
                    ('Ski Erg', 1, None, None, None, None, 10, None, 'Round B — 10 cal'),
                    ('DB Burpee Deadlift', 2, 35, 15, None, None, None, None, 'Round B — 15 reps @ 30-40 lbs'),
                    ('Ski Erg', 2, None, None, None, None, 10, None, 'Round B — 10 cal'),
                ],
            },
            {
                'name': 'Block B — Strength',
                'order': 2,
                # Bent Over Row scheme: 6 all sets; KB Tricep Ext: 12 all sets
                # 12kg = 26.5 lbs
                'scheme': '5 Sets | RPE 7-8 | Every 2:30',
                'sets': [
                    ('Bent Over Row', 1, 85, 6, 7.5, None, None, None, None),
                    ('Tricep Extension', 1, 26.5, 12, 7.5, None, None, None, '~12kg blue'),
                    ('Bent Over Row', 2, 95, 6, 7.5, None, None, None, None),
                    ('Tricep Extension', 2, 26.5, 12, 7.5, None, None, None, '~12kg blue'),
                    ('Bent Over Row', 3, 95, 6, 7.5, None, None, None, None),
                    ('Tricep Extension', 3, 26.5, 12, 7.5, None, None, None, '~12kg blue'),
                    ('Bent Over Row', 4, 115, 6, 7.5, None, None, None, None),
                    ('Tricep Extension', 4, 26.5, 12, 7.5, None, None, None, '~12kg blue'),
                    ('Bent Over Row', 5, 115, 6, 7.5, None, None, None, None),
                    ('Tricep Extension', 5, 26.5, 12, 7.5, None, None, None, '~12kg blue'),
                ],
            },
            {
                'name': 'Block C — Strength',
                'order': 3,
                # Pull Up scheme: 6; Arnold Press: 6,6; Hollow Hold: 20 secs
                'scheme': '4 Sets | RPE 7-8 | Every 3:00',
                'sets': [
                    ('Pull-ups', 1, None, 6, 7.5, None, None, None, 'BW'),
                    ('Arnold Press', 1, 20, 6, 7.5, None, None, None, None),
                    ('Hollow Hold', 1, 10, None, None, 20, None, None, '10 lbs plate, 20 secs'),
                    ('Pull-ups', 2, None, 6, 7.5, None, None, None, 'BW'),
                    ('Arnold Press', 2, 20, 6, 7.5, None, None, None, None),
                    ('Hollow Hold', 2, 15, None, None, 20, None, None, '15 lbs plate, 20 secs'),
                    ('Pull-ups', 3, None, 4, 7.5, None, None, None, 'BW'),
                    ('Arnold Press', 3, 25, 6, 7.5, None, None, None, None),
                    ('Hollow Hold', 3, 15, None, None, 20, None, None, '15 lbs plate, 20 secs'),
                    # Set 4: no pull-ups, Arnold Press 30 lbs × 5 reps
                    ('Arnold Press', 4, 30, 5, 7.5, None, None, None, '30×5'),
                    ('Hollow Hold', 4, 15, None, None, 20, None, None, '15 lbs plate, 20 secs'),
                    # Set 5: no pull-ups, Arnold Press 30 lbs × 4 reps (9 total)
                    ('Arnold Press', 5, 30, 4, 7.5, None, None, None, '30×4 (9 total)'),
                    ('Hollow Hold', 5, 15, None, None, 20, None, None, '15 lbs plate, 20 secs'),
                    # Banded pull-ups to finish (extra set)
                    ('Pull-ups', 4, None, 6, None, None, None, None, 'Banded, blue band'),
                ],
            },
            {
                'name': 'Finisher — Core Strength',
                'order': 4,
                'scheme': 'EMOM × 4',
                'sets': [
                    ('KB Windmill', 1, None, None, None, 60, None, None, 'H/K KB Windmill Left, 1 min'),
                    ('KB Windmill', 2, None, None, None, 60, None, None, 'H/K KB Windmill Right, 1 min'),
                    ('KB Windmill', 3, None, None, None, 60, None, None, 'H/K KB Windmill Left, 1 min'),
                    ('KB Windmill', 4, None, None, None, 60, None, None, 'H/K KB Windmill Right, 1 min'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-27 — AC Upper W12
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-27',
        'sleep_hours': None,
        'tags': ['ac', 'upper', 'strength'],
        'notes': 'Strength Club session — not regular MPA squad',
        'blocks': [
            {
                'name': 'Block A — Strength',
                'order': 1,
                # Alt DB Bridged Floor Press: 16 reps; Incline Bench DB Prone Row: 10 reps
                # Set 1: 30 lbs floor press (12 both then 4 alt = 16 total), 30 lbs row
                # Sets 2-4: 35 lbs × 16 alt
                'scheme': '4 Sets | RPE 7-8 | Every 3:00',
                'sets': [
                    ('DB Floor Press', 1, 30, 16, 7.5, None, None, None, 'Set 1: 30×12 then 30×4 alt'),
                    ('Incline Prone Row', 1, 30, 10, 7.5, None, None, None, None),
                    ('DB Floor Press', 2, 35, 16, 7.5, None, None, None, 'Alt'),
                    ('Incline Prone Row', 2, 30, 10, 7.5, None, None, None, None),
                    ('DB Floor Press', 3, 35, 16, 7.5, None, None, None, 'Alt'),
                    ('Incline Prone Row', 3, 30, 10, 7.5, None, None, None, None),
                    ('DB Floor Press', 4, 35, 16, 7.5, None, None, None, 'Alt'),
                    ('Incline Prone Row', 4, 30, 10, 7.5, None, None, None, None),
                ],
            },
            {
                'name': 'Block B — Strength',
                'order': 2,
                # BB Strict Press: 6 reps; Gorilla Row: 10 reps
                'scheme': '4 Sets | RPE 7-8 | Every 3:00',
                'sets': [
                    ('Strict Press', 1, 45, 6, 7.5, None, None, None, None),
                    ('Gorilla Row', 1, 35, 10, 7.5, None, None, None, None),
                    ('Strict Press', 2, 55, 6, 7.5, None, None, None, None),
                    ('Gorilla Row', 2, 35, 10, 7.5, None, None, None, None),
                    ('Strict Press', 3, 65, 6, 7.5, None, None, None, None),
                    ('Gorilla Row', 3, 45, 10, 7.5, None, None, None, None),
                    ('Strict Press', 4, 65, 6, 7.5, None, None, None, None),
                    ('Gorilla Row', 4, 45, 10, 7.5, None, None, None, None),
                ],
            },
            {
                'name': 'Block C — Strength',
                'order': 3,
                # Renegade Row: 12 reps; Alt DB Hammer Curl: 16 reps
                'scheme': '4 Sets | RPE 7-8 | Every 3:00',
                'sets': [
                    ('Renegade Row', 1, 15, 12, 7.5, None, None, None, 'No push-up'),
                    ('Hammer Curl', 1, 20, 16, 7.5, None, None, None, 'Alt'),
                    # Set 2: 20 × 6 (no push-up) + 15 × 6 (with push-up)
                    ('Renegade Row', 2, 20, 6, 7.5, None, None, None, 'No push-up, first half'),
                    ('Renegade Row', 3, 15, 6, 7.5, None, None, None, 'With push-up, second half'),
                    ('Hammer Curl', 2, 20, 16, 7.5, None, None, None, 'Alt'),
                    # Sets 3-4: 12.5 lbs with push-up
                    ('Renegade Row', 4, 12.5, 12, 7.5, None, None, None, 'With push-up'),
                    ('Hammer Curl', 3, 20, 16, 7.5, None, None, None, 'Alt'),
                    ('Renegade Row', 5, 12.5, 12, 7.5, None, None, None, 'With push-up'),
                    ('Hammer Curl', 4, 20, 16, 7.5, None, None, None, 'Alt'),
                ],
            },
            {
                'name': 'Finisher — Core Strength',
                'order': 4,
                'scheme': '4:00 Min Continuous | 2-4-6-8-10-12-14-16...',
                'sets': [
                    ('Plank', 1, None, None, None, 180, None, None, 'Tall plank knee to elbow + deadbug ~3 min'),
                    ('Deadbug', 1, None, None, None, 180, None, None, 'Slow + controlled'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-03-31 — MPA Upper Test
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-03-31',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'upper', 'test'],
        'notes': 'Test week — bench press 3RM is the main event. 3RM Result: 115 lbs.',
        'blocks': [
            {
                'name': 'Block A — Conditioning TEST',
                'order': 1,
                'scheme': 'Teams of 3 | Max Meters',
                'sets': [
                    # Warm up: 2:30 min row
                    ('Row Erg', 1, None, None, None, 150, None, None, 'Warm up 2:30 min'),
                    # Sprint test: 15 cal at 1700 cal/hr pace
                    ('Row Erg', 2, None, None, None, None, 15, None, 'Sprint test 15 cal @ 1700 cal/hr pace'),
                    # Ski test: 150m
                    ('Ski Erg', 1, None, None, None, None, None, None, 'Ski test 150m'),
                    # Team max meters: 25 cal at 1100 cal/hr pace on row
                    ('Row Erg', 3, None, None, None, None, 25, None, 'Team max meters 25 cal'),
                ],
            },
            {
                'name': 'Block B — Bench Press 3RM Test',
                'order': 2,
                'scheme': '5 Sets | RPE 10 | Build to 3RM',
                'sets': [
                    ('Bench Press', 1, 95, 5, 6, None, None, None, 'RPE 6'),
                    ('Bench Press', 2, 115, 3, 7.5, None, None, None, 'RPE 7.5'),
                    # Set 3: 125 lbs, ×2 attempted but failed on 2nd rep
                    ('Bench Press', 3, 125, 2, None, None, None, None, 'Failed on 2nd rep'),
                    # Set 4: 115 lbs, ×3, 3RM
                    ('Bench Press', 4, 115, 3, 9.75, None, None, None, '3RM'),
                ],
            },
            {
                'name': 'Block C — Prime/Accessory',
                'order': 3,
                # DB Row: 8 reps; DB Pullover: 8 reps; External Rotation: 8,8
                'scheme': '4 Sets | RPE 7.5 | Every 3:00',
                'sets': [
                    ('Bent Over Row', 1, 30, 8, 7.5, None, None, None, 'DB Bent Over Row'),
                    ('DB Pullover', 1, 25, 8, 7.5, None, None, None, 'Hollow Body'),
                    ('External Rotation', 1, 10, 8, 7.5, None, None, None, None),
                    ('Bent Over Row', 2, 35, 8, 7.5, None, None, None, 'DB Bent Over Row'),
                    ('DB Pullover', 2, 30, 8, 7.5, None, None, None, 'Hollow Body'),
                    ('External Rotation', 2, 12.5, 8, 7.5, None, None, None, None),
                    ('Bent Over Row', 3, 40, 8, 7.5, None, None, None, 'DB Bent Over Row'),
                    ('DB Pullover', 3, 30, 8, 7.5, None, None, None, 'Hollow Body'),
                    ('External Rotation', 3, 10, 8, 7.5, None, None, None, None),
                    ('Bent Over Row', 4, 40, 8, 7.5, None, None, None, 'DB Bent Over Row'),
                    ('DB Pullover', 4, 30, 8, 7.5, None, None, None, 'Hollow Body'),
                    ('External Rotation', 4, 10, 8, 7.5, None, None, None, None),
                ],
            },
            {
                'name': 'Finisher — Core Strength',
                'order': 4,
                'scheme': 'EMOM × 4',
                'sets': [
                    ('Pull Through', 1, None, None, None, 30, None, None, 'KB Bear Plank Pull Through, 30 secs'),
                    ('Hollow Hold', 1, None, None, None, 20, None, None, '20 secs'),
                    ('Pull Through', 2, None, None, None, 30, None, None, 'KB Bear Plank Pull Through, 30 secs'),
                    ('Hollow Hold', 2, None, None, None, 20, None, None, '20 secs'),
                ],
            },
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # 2026-04-02 — MPA Lower Test
    # ──────────────────────────────────────────────────────────────────────────
    {
        'date': '2026-04-02',
        'sleep_hours': None,
        'tags': ['mpa', 'squad', 'lower', 'test'],
        'notes': 'Test week — back squat 3RM. 3RM Result: 175 lbs PR.',
        'blocks': [
            {
                'name': 'Block A — Prime/Accessory',
                'order': 1,
                # KB Swing: 5 reps; DB RDL: 10 reps; Calf Raise: 15 reps
                # 20kg = 44.1 lbs for KB Swing
                'scheme': '4 Sets | RPE 7.5 | Every 3:00',
                'sets': [
                    ('KB Swing', 1, 44.1, 5, 7.5, None, None, None, '20kg (44 lbs)'),
                    ('DB RDL', 1, 35, 10, 7.5, None, None, None, None),
                    ('Calf Raise', 1, None, 15, 7.5, None, None, None, 'Double leg'),
                    ('KB Swing', 2, 44.1, 5, 7.5, None, None, None, '20kg (44 lbs)'),
                    ('DB RDL', 2, 30, 10, 7.5, None, None, None, None),
                    ('Calf Raise', 2, None, 15, 7.5, None, None, None, 'Double leg'),
                    ('KB Swing', 3, 44.1, 5, 7.5, None, None, None, '20kg (44 lbs)'),
                    ('DB RDL', 3, 30, 10, 7.5, None, None, None, None),
                    ('Calf Raise', 3, None, 15, 7.5, None, None, None, 'Double leg'),
                    # Set 4: back flagged — stopped DB RDL early (half set)
                    ('KB Swing', 4, 44.1, 5, 7.5, None, None, None, '20kg (44 lbs)'),
                    ('DB RDL', 4, 30, 5, 7.5, None, None, None, 'Back flagged — half set'),
                    ('Calf Raise', 4, None, 15, 7.5, None, None, None, 'Double leg'),
                ],
            },
            {
                'name': 'Block B — Back Squat 3RM Test',
                'order': 2,
                'scheme': '5 Sets | RPE 9.5 | Build to 3RM',
                'sets': [
                    ('Back Squat', 1, 95, 5, 5, None, None, None, 'RPE 5'),
                    ('Back Squat', 2, 115, 3, 6, None, None, None, 'RPE 6'),
                    ('Back Squat', 3, 135, 2, 7, None, None, None, 'RPE 7'),
                    ('Back Squat', 4, 155, 1, 7.5, None, None, None, 'RPE 7.5'),
                    ('Back Squat', 5, 175, 3, 9.5, None, None, None, '3RM PR — last 2 reps sketchy'),
                ],
            },
            {
                'name': 'Block C — Conditioning',
                'order': 3,
                # Ski/Bike: 8 cal each round; DB Clean Press: 16 reps @ 25 lbs (scaled)
                'scheme': 'Every 2:30 + 30 sec rest × 4 (In Pairs)',
                'sets': [
                    # Round 1: Ski cal + DB Clean Press + max ski
                    ('Ski Erg', 1, None, None, None, None, 8, None, 'Round 1 — 8 cal ski'),
                    ('DB Power Clean to Press', 1, 25, 16, None, None, None, None, 'Round 1'),
                    # Round 2: Ski
                    ('Ski Erg', 2, None, None, None, None, 8, None, 'Round 2 — 8 cal ski'),
                    ('DB Power Clean to Press', 2, 25, 16, None, None, None, None, 'Round 2'),
                    # Round 3: Bike
                    ('Echo Bike', 1, None, None, None, None, 8, None, 'Round 3 — 8 cal bike'),
                    ('DB Power Clean to Press', 3, 25, 16, None, None, None, None, 'Round 3'),
                    # Round 4: Bike
                    ('Echo Bike', 2, None, None, None, None, 8, None, 'Round 4 — 8 cal bike'),
                    ('DB Power Clean to Press', 4, 25, 16, None, None, None, None, 'Round 4'),
                ],
            },
            {
                'name': 'Finisher — Core Strength',
                'order': 4,
                'scheme': 'EMOM × 4',
                'sets': [
                    ('Russian Twist', 1, None, None, None, 60, None, None, 'Weight Plate Russian Twist, 1 min'),
                    ('Sit-up', 1, None, None, None, 60, None, None, 'Weight Plate Sit Up, 1 min'),
                    ('Russian Twist', 2, None, None, None, 60, None, None, 'Weight Plate Russian Twist, 1 min'),
                    ('Sit-up', 2, None, None, None, 60, None, None, 'Weight Plate Sit Up, 1 min'),
                ],
            },
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Alias map for exercise name normalization
# ──────────────────────────────────────────────────────────────────────────────

ALIASES = {
    'back squat': 'Back Squat',
    'bench press': 'Bench Press',
    'deadlift': 'Deadlift',
    'strict press': 'Strict Press',
    'pull-ups': 'Pull-ups',
    'chin-up': 'Chin-up',
    'pendlay row': 'Pendlay Row',
    'kb pendlay row': 'KB Pendlay Row',
    'bent over row': 'Bent Over Row',
    'bulgarian split squat': 'Bulgarian Split Squat',
    'kb rdl': 'KB RDL',
    'db rdl': 'DB RDL',
    'glute bridge': 'Glute Bridge',
    'row erg': 'Row Erg',
    'ski erg': 'Ski Erg',
    'echo bike': 'Echo Bike',
    "farmer's carry": "Farmer's Carry",
    'kb swing': 'KB Swing',
    'goblet squat': 'Goblet Squat',
    'db shoulder press': 'DB Shoulder Press',
    'arnold press': 'Arnold Press',
    'lat pulldown': 'Lat Pulldown',
    'dips': 'Dips',
    'push-up': 'Push-up',
    'gorilla row': 'Gorilla Row',
    'renegade row': 'Renegade Row',
    'db floor press': 'DB Floor Press',
    'db pullover': 'DB Pullover',
    'reverse row': 'Reverse Row',
    'plank': 'Plank',
    'sit-up': 'Sit-up',
    'front rack squat': 'Front Rack Squat',
    'cyclist squat': 'Cyclist Squat',
    'burpee': 'Burpee',
    'db high pull': 'DB High Pull',
    'db snatch': 'DB Snatch',
    'db burpee deadlift': 'DB Burpee Deadlift',
    'plate g2oh': 'Plate G2OH',
    'russian twist': 'Russian Twist',
    'kb windmill': 'KB Windmill',
    'pull through': 'Pull Through',
    'hollow hold': 'Hollow Hold',
    'deadbug': 'Deadbug',
    'external rotation': 'External Rotation',
    'reverse lunge': 'Reverse Lunge',
    'step-up': 'Step-up',
    'box jump': 'Box Jump',
    'kb plank row': 'KB Plank Row',
    'calf raise': 'Calf Raise',
    'hammer curl': 'Hammer Curl',
    'tricep extension': 'Tricep Extension',
    'kb toe touch': 'KB Toe Touch',
    'incline prone row': 'Incline Prone Row',
    'banded deadlift': 'Banded Deadlift',
    'reverse leg raise': 'Reverse Leg Raise',
    'push press': 'Push Press',
    'db power clean to press': 'DB Power Clean to Press',
    'plate pass': 'Plate Pass',
}


def normalize(name: str) -> str:
    key = name.strip().lower()
    if key in ALIASES:
        return ALIASES[key]
    return name.strip().title()


def get_or_create_exercise(cur: sqlite3.Cursor, name: str) -> int:
    canonical = normalize(name)
    cur.execute('SELECT id FROM exercises WHERE name = ?', (canonical,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute('INSERT INTO exercises (name) VALUES (?)', (canonical,))
    return cur.lastrowid


def main() -> None:
    if not DB_PATH.exists():
        print(f'ERROR: DB not found at {DB_PATH}')
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Wipe existing data in correct FK order
    print('Wiping existing data...')
    cur.execute('DELETE FROM sets')
    cur.execute('DELETE FROM blocks')
    cur.execute('DELETE FROM workouts')
    cur.execute('DELETE FROM exercises')
    conn.commit()
    print('Done.')

    total_workouts = 0
    total_blocks = 0
    total_sets = 0

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    for w in WORKOUTS:
        date = w['date']
        name = WORKOUT_NAMES[date]
        tags = json.dumps(w.get('tags') or [])
        notes = w.get('notes')
        sleep = w.get('sleep_hours')

        cur.execute(
            'INSERT INTO workouts (name, date, sleep_hours, tags, notes) VALUES (?,?,?,?,?)',
            (name, date, sleep, tags, notes),
        )
        workout_id = cur.lastrowid
        total_workouts += 1

        for block in w['blocks']:
            cur.execute(
                'INSERT INTO blocks (workout_id, name, "order", scheme) VALUES (?,?,?,?)',
                (workout_id, block['name'], block['order'], block.get('scheme')),
            )
            block_id = cur.lastrowid
            total_blocks += 1

            for s in block['sets']:
                ex_name, rnd, weight, reps, rpe, duration, calories, watts, set_notes = s
                exercise_id = get_or_create_exercise(cur, ex_name)
                cur.execute(
                    '''INSERT INTO sets
                       (block_id, exercise_id, round, weight_lbs, reps, rpe,
                        duration_secs, calories, watts, notes, logged_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                    (block_id, exercise_id, rnd, weight, reps, rpe,
                     duration, calories, watts, set_notes, now),
                )
                total_sets += 1

    conn.commit()
    conn.close()

    print(f'\n✅ Import complete!')
    print(f'   Workouts : {total_workouts}')
    print(f'   Blocks   : {total_blocks}')
    print(f'   Sets     : {total_sets}')

    # Print per-workout summary
    conn2 = sqlite3.connect(DB_PATH)
    cur2 = conn2.cursor()
    print('\nPer-workout set counts:')
    cur2.execute('''
        SELECT w.date, w.name, COUNT(s.id) as set_count
        FROM workouts w
        JOIN blocks b ON b.workout_id = w.id
        JOIN sets s ON s.block_id = b.id
        GROUP BY w.id
        ORDER BY w.date
    ''')
    for row in cur2.fetchall():
        print(f'  {row[0]}  {row[1]:<35}  {row[2]} sets')
    conn2.close()


if __name__ == '__main__':
    main()
