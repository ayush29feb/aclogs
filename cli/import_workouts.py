#!/usr/bin/env python3
"""
One-off script to import historical workout data from markdown files into gym.db.
"""

from __future__ import annotations

import re
import os
import glob
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Tuple

DB_PATH = Path(__file__).parent / "gym.db"

# ──────────────────────────────────────────────────────────────────────────────
# Exercise name normalization
# ──────────────────────────────────────────────────────────────────────────────

ALIASES = {
    "bb back squat": "Back Squat",
    "back squat": "Back Squat",
    "barbell back squat": "Back Squat",
    "bb bench press": "Bench Press",
    "bench press": "Bench Press",
    "bb deadlift": "Deadlift",
    "deadlift": "Deadlift",
    "bb strict press": "Strict Press",
    "bb overhead press": "Strict Press",
    "pull up": "Pull-ups",
    "pull ups": "Pull-ups",
    "pull-up": "Pull-ups",
    "pull-ups": "Pull-ups",
    "weighted pull up": "Pull-ups",
    "pull ups (weighted)": "Pull-ups",
    "chin up": "Chin-up",
    "chin ups": "Chin-up",
    "chin-up": "Chin-up",
    "chin-ups": "Chin-up",
    "pendlay row": "Pendlay Row",
    "bb pendlay row": "Pendlay Row",
    "kb pendlay row": "KB Pendlay Row",
    "explosive kb pendlay row": "KB Pendlay Row",
    "bent over row": "Bent Over Row",
    "bb bent over row": "Bent Over Row",
    "bb row": "Bent Over Row",
    "bent over supinated to pronated row": "Bent Over Row",
    "db bent over row": "Bent Over Row",
    "bulgarian split squat": "Bulgarian Split Squat",
    "split squat": "Bulgarian Split Squat",
    "kb cross body rdl": "RDL",
    "rdl": "RDL",
    "romanian deadlift": "RDL",
    "db rdl": "DB RDL",
    "db romanian deadlift": "DB RDL",
    "glute bridge": "Glute Bridge",
    "bb glute bridge": "Glute Bridge",
    "rowing": "Row Erg",
    "row erg": "Row Erg",
    "c2 row": "Row Erg",
    "ski erg": "Ski Erg",
    "ski": "Ski Erg",
    "echo bike": "Echo Bike",
    "c2 bike": "Echo Bike",
    "assault bike": "Echo Bike",
    "farmer's carry": "Farmer's Carry",
    "farmers carry": "Farmer's Carry",
    "kb swing": "KB Swing",
    "kb deadstop swing": "KB Swing",
    "heavy dual deadstop kb swing": "KB Swing",
    "dead stop kb swing": "KB Swing",
    "dual deadstop kb swing": "KB Swing",
    "goblet squat": "Goblet Squat",
    "db shoulder press": "DB Shoulder Press",
    "h/k db shoulder press": "DB Shoulder Press",
    "arnold press": "Arnold Press",
    "seated alt arnold press": "Arnold Press",
    "lat pulldown": "Lat Pulldown",
    "dips": "Dips",
    "dip": "Dips",
    "push up": "Push-up",
    "push ups": "Push-up",
    "ring push up": "Push-up",
    "kb push up": "Push-up",
    "incline plyo push up": "Push-up",
    "gorilla row": "Gorilla Row",
    "dual gorilla row": "Gorilla Row",
    "renegade row": "Renegade Row",
    "db chest press": "DB Floor Press",
    "db floor press": "DB Floor Press",
    "db bridged floor press": "DB Floor Press",
    "alt db bridged floor press": "DB Floor Press",
    "db pullover": "DB Pullover",
    "hollow body db pullover": "DB Pullover",
    "reverse row": "Reverse Row",
    "plank": "Plank",
    "weighted plank": "Plank",
    "tall plank": "Plank",
    "atomic sit-up": "Sit-up",
    "sit up": "Sit-up",
    "sit ups": "Sit-up",
    "weighted sit-up": "Sit-up",
    "sit ups (weighted)": "Sit-up",
    "front rack squat": "Front Rack Squat",
    "cyclist squat": "Cyclist Squat",
    "burpee": "Burpee",
    "burpees": "Burpee",
    "burpee to plate": "Burpee",
    "db high pull": "DB High Pull",
    "db snatch": "DB Snatch",
    "dual db snatch": "DB Snatch",
    "db burpee deadlift": "DB Burpee Deadlift",
    "plate ground to overhead": "Plate Ground to Overhead",
    "weight plate russian twist": "Russian Twist",
    "russian twist": "Russian Twist",
    "kb windmill": "KB Windmill",
    "h/k kb windmill": "KB Windmill",
    "kb bear plank pull through": "Pull Through",
    "pull through": "Pull Through",
    "hollow hold": "Hollow Hold",
    "hollow body": "Hollow Hold",
    "weight plate hollow hold": "Hollow Hold",
    "deadbug": "Deadbug",
    "external rotation": "External Rotation",
    "reverse lunge": "Reverse Lunge",
    "deficit reverse lunge": "Reverse Lunge",
    "db alt reverse lunge": "Reverse Lunge",
    "b/r forward lunge": "Reverse Lunge",
    "goblet reverse lunge": "Reverse Lunge",
    "step up": "Step-up",
    "kb front rack step up": "Step-up",
    "box jump": "Box Jump",
    "seated box jump": "Box Jump",
    "hurdle to box jump": "Box Jump",
    "kb box plank row": "KB Plank Row",
    "box plank kb row": "KB Plank Row",
    "calf raise": "Calf Raise",
    "double leg calf raise": "Calf Raise",
    "db hammer curl": "Hammer Curl",
    "alt db hammer curl": "Hammer Curl",
    "tricep extension": "Tricep Extension",
    "kb horn z seated tricep extension": "Tricep Extension",
    "kb toe touch": "KB Toe Touch",
    "supine kb toe touch": "KB Toe Touch",
    "banded deadlift": "Deadlift",
    "row": "Row Erg",
    "c2 bike": "Echo Bike",
    "gorilla rows": "Gorilla Row",
    # Column header derived names (lowercase from table parsing)
    "db row": "Bent Over Row",
    "prone row": "Bent Over Row",
    "incline bench db prone row": "Bent Over Row",
    "kb row": "KB Plank Row",
    "ext. rotation": "External Rotation",
    "hammer curl": "Hammer Curl",
    "kb tricep ext": "Tricep Extension",
    "tricep ext": "Tricep Extension",
    # Misc normalizations
    "rowing conditioning": "Row Erg",
    "(heavy) db rdl": "DB RDL",
    "(heavy) deadball squat": "Goblet Squat",
    "deadball squat": "Goblet Squat",
    "bench": "Bench Press",
    "bench w/ legs raised": "Bench Press",
    "squat": "Back Squat",
    "knee push up": "Push-up",
    "plate pass": "Plate Ground to Overhead",
    "push press": "Push Press",
    "reverse leg raises": "Reverse Leg Raises",
}

# Strip common prefixes from block headings to get exercise name
STRIP_PREFIXES = ["BB ", "KB ", "DB ", "Weighted "]

def normalize_exercise(name: str) -> str:
    """Normalize an exercise name using the alias table."""
    stripped = re.sub(r"\*\*", "", name).strip()
    # Remove parenthetical qualifiers like "(Eccentric Focus)", "(weighted)", "(Tempo)"
    clean = re.sub(r"\s*\([^)]*\)\s*$", "", stripped).strip()
    lower = clean.lower()
    if lower in ALIASES:
        return ALIASES[lower]
    # Also try stripping trailing descriptors
    lower2 = stripped.lower()
    if lower2 in ALIASES:
        return ALIASES[lower2]
    return clean if clean else stripped


def extract_exercise_from_block(block_name: str) -> str:
    """
    Extract exercise name from block heading like:
    'Block B — BB Back Squat' → 'Back Squat'
    'Primary — Bench Press' → 'Bench Press'
    'Deadlift — Max Test' → 'Deadlift'
    'Bench Press (Eccentric Focus)' → 'Bench Press'
    'Block B — BACK SQUAT 3RM TEST' → 'Back Squat'
    """
    name = block_name.strip()
    # Split on " — " (em dash with spaces) or " – " (en dash) or " - "
    for sep in [" — ", " – ", " - "]:
        if sep in name:
            parts = name.split(sep, 1)
            left = parts[0].strip()
            right = parts[1].strip()
            # If right looks like a descriptor, use left as exercise name
            descriptors = {
                "max test", "speed", "working sets", "intervals", "conditioning",
                "tempo", "50m", "partial", "metcon", "core emom",
                "emom × 4", "emom x 4", "emom × 12", "emom x 12",
            }
            right_lower = right.lower()
            # Right side is a descriptor if:
            # - explicitly in descriptor set
            # - starts with "max " and is short
            # - is an all-caps phrase with no spaces matching exercise pattern
            # - ends in "3rm test", "1rm test" etc.
            is_descriptor = (
                right_lower in descriptors
                or (right_lower.startswith("max") and len(right) < 25)
                or re.search(r"\d+rm test", right_lower) is not None
                or right_lower in ("speed", "working sets", "intervals", "imt", "iwt",
                                   "e4mom × 12", "emom × 12")
            )
            if is_descriptor:
                # But if right side has exercise embedded (like "BENCH PRESS 3RM TEST"),
                # try to extract the exercise from the right side first
                m_3rm = re.match(r"^(.+?)\s+\d+RM\s+TEST$", right, re.IGNORECASE)
                if m_3rm:
                    # "BENCH PRESS 3RM TEST" → "BENCH PRESS" → normalize
                    name = m_3rm.group(1).strip()
                else:
                    name = left
            else:
                name = right
            break

    # Strip known block prefixes: "Block A", "Block B", "Primary", "Secondary", etc.
    name = re.sub(r"^Block\s+[A-Z]\s*$", "", name).strip()
    name = re.sub(r"^(Primary|Secondary|Prime|Warm Up|Finisher)\s*$", "", name, flags=re.IGNORECASE).strip()

    # Handle "X 3RM TEST" or "X 1RM TEST" → extract just exercise name (fallback)
    m = re.match(r"^(.+?)\s+\d+RM TEST$", name, re.IGNORECASE)
    if m:
        name = m.group(1).strip()

    # Handle ALLCAPS names: "BACK SQUAT 3RM TEST" → "Back Squat"
    if name.isupper() and len(name) > 3:
        name = name.title()

    result = normalize_exercise(name)
    # Fallback: if result is empty, return the original block name
    return result if result else block_name.strip()


# ──────────────────────────────────────────────────────────────────────────────
# Parsing helpers
# ──────────────────────────────────────────────────────────────────────────────

def strip_md_bold(s: str) -> str:
    return re.sub(r"\*\*", "", s).strip()


def parse_weight_lbs(s: str) -> Optional[float]:
    """Parse weight string → float lbs or None."""
    if not s:
        return None
    s = strip_md_bold(s).strip()
    if s in ("—", "-", "", "BW", "Bodyweight", "bodyweight", "bw"):
        return None
    # Match "N lbs" or "N lbs x2" etc.
    m = re.match(r"^\+?(\d+(?:\.\d+)?)\s*lbs?", s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    # "Nkg" or "N kg"
    m = re.match(r"^~?(\d+(?:\.\d+)?)\s*kg", s, re.IGNORECASE)
    if m:
        return round(float(m.group(1)) * 2.20462, 1)
    # "N (yellow KB)" etc
    m = re.match(r"^~?(\d+(?:\.\d+)?)\s*\(", s)
    if m:
        return float(m.group(1))
    # Plain number
    m = re.match(r"^~?(\d+(?:\.\d+)?)$", s)
    if m:
        return float(m.group(1))
    # "N lbs x2" - just take the number
    m = re.match(r"^~?(\d+(?:\.\d+)?)\s*lbs?\s*x\d+", s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def parse_reps(s: str) -> Optional[int]:
    """Parse reps string → int or None."""
    if not s:
        return None
    s = strip_md_bold(s).strip()
    if s in ("—", "-", "", "BW"):
        return None
    # "×5" or "x5"
    m = re.match(r"^[×x](\d+)", s)
    if m:
        return int(m.group(1))
    # "5 (fast)" or "3 (x2)"
    m = re.match(r"^(\d+)\s*[\(\[]", s)
    if m:
        return int(m.group(1))
    # "5/5" (bilateral) — take first
    m = re.match(r"^(\d+)/\d+", s)
    if m:
        return int(m.group(1))
    # "5 x 3" — sets×reps: take reps (right side)
    m = re.match(r"^(\d+)\s*[x×]\s*(\d+)", s, re.IGNORECASE)
    if m:
        return int(m.group(2))
    # Plain int
    m = re.match(r"^(\d+)", s)
    if m:
        return int(m.group(1))
    return None


def parse_rpe(s: str) -> Optional[float]:
    """Parse RPE string like 'RPE 8', '9.5/10', '8' → float."""
    if not s:
        return None
    s = strip_md_bold(s).strip()
    if s in ("—", "-", ""):
        return None
    m = re.match(r"(?:RPE\s*)?(\d+(?:\.\d+)?)", s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def parse_watts(s: str) -> Optional[float]:
    """Parse watts from string like '200W', '199W'."""
    if not s:
        return None
    s = strip_md_bold(s).strip()
    m = re.search(r"(\d+(?:\.\d+)?)\s*W\b", s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def parse_calories(s: str) -> Optional[float]:
    """Parse calories from a string."""
    if not s:
        return None
    s = strip_md_bold(s).strip()
    m = re.search(r"(\d+(?:\.\d+)?)\s*cal", s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def parse_set_range(s: str) -> list[int]:
    """Parse set descriptor like '1', '1-3', '2-4' → list of set numbers."""
    s = strip_md_bold(s).strip()
    m = re.match(r"^(\d+)-(\d+)$", s)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    m = re.match(r"^(\d+)$", s)
    if m:
        return [int(m.group(1))]
    return [1]


# ──────────────────────────────────────────────────────────────────────────────
# Markdown table parsing
# ──────────────────────────────────────────────────────────────────────────────

def parse_md_table(lines: list[str]) -> list[dict]:
    """
    Parse a markdown table into a list of dicts (header → cell).
    Skips separator lines (---|---).
    """
    rows = []
    headers = None
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if headers is None:
            headers = [h.lower().strip() for h in cells]
            continue
        # Skip separator rows
        if all(re.match(r"^[-:]+$", c) for c in cells if c):
            continue
        row = {}
        for i, h in enumerate(headers):
            row[h] = cells[i] if i < len(cells) else ""
        rows.append(row)
    return rows


def find_col(row: dict, candidates: list[str]) -> str | None:
    """Find first matching column value from candidates list."""
    for c in candidates:
        if c in row:
            return row[c]
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Tag derivation
# ──────────────────────────────────────────────────────────────────────────────

def derive_tags_from_filename(filename: str) -> list[str]:
    fn = filename.lower()
    tags = []
    if "upper" in fn:
        tags.append("upper")
    if "lower" in fn:
        tags.append("lower")
    if "mpa" in fn or "squad" in fn:
        tags.append("squad")
    if "aps" in fn:
        tags.append("aps")
    if "test" in fn:
        tags.append("test")
    if "deload" in fn:
        tags.append("deload")
    if "ac" in fn or "strength" in fn:
        tags.append("strength")
    return tags


def parse_tags_line(line: str) -> list[str]:
    """Parse '#tag1 #tag2' from a tags line."""
    tags = re.findall(r"#(\w+)", line)
    return tags


# ──────────────────────────────────────────────────────────────────────────────
# Main file parser
# ──────────────────────────────────────────────────────────────────────────────

def parse_workout_file(filepath: str) -> dict:
    """Parse a workout markdown file into structured data."""
    path = Path(filepath)
    filename = path.name

    # Date from filename prefix
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    date = m.group(1) if m else None

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # Parse name from first # heading
    name = filename
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            name = stripped[2:].strip()
            break

    # Parse sleep
    sleep_hours = None
    for line in lines:
        m = re.search(r"\*\*Sleep:\*\*\s*([\d.]+)", line)
        if m:
            sleep_hours = float(m.group(1))
            break

    # Parse tags
    tags = []
    for line in lines:
        if re.search(r"\*\*Tags:\*\*", line):
            tags = parse_tags_line(line)
            break
    if not tags:
        tags = derive_tags_from_filename(filename)

    # Parse notes (from **Notes:** line or ## Notes section)
    notes_lines = []
    in_notes_section = False
    for line in lines:
        # Check for ## Notes heading
        if re.match(r"^##\s+Notes\s*$", line.strip()):
            in_notes_section = True
            continue
        if in_notes_section:
            if re.match(r"^##", line.strip()):
                break
            notes_lines.append(line)
        # Also check **Notes:** inline
        m = re.match(r"\*\*Notes?:\*\*\s*(.*)", line)
        if m and not in_notes_section:
            val = m.group(1).strip()
            if val:
                notes_lines.append(val)
    notes = "\n".join(notes_lines).strip() or None

    # Parse blocks (## headings)
    blocks = []
    current_block = None
    current_lines = []

    def flush_block():
        nonlocal current_block, current_lines
        if current_block is not None:
            blocks.append({"name": current_block, "lines": list(current_lines)})
        current_block = None
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^## (.+)", stripped):
            flush_block()
            heading = re.match(r"^## (.+)", stripped).group(1).strip()
            # Skip "Notes" / "Summary" sections as blocks
            if heading.lower() not in ("notes", "summary"):
                current_block = heading
        elif current_block is not None:
            current_lines.append(line)

    flush_block()

    return {
        "date": date,
        "name": name,
        "sleep_hours": sleep_hours,
        "tags": tags,
        "notes": notes,
        "blocks": blocks,
        "filepath": filepath,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Set extraction from a block
# ──────────────────────────────────────────────────────────────────────────────

def extract_sets_from_block(block_name: str, block_lines: list[str]) -> list[dict]:
    """
    Extract set records from a block's content lines.
    Returns list of dicts with keys:
      exercise, round, weight_lbs, reps, rpe, duration_secs, distance_m, calories, watts, notes
    """
    sets = []

    # Split lines into table chunks
    table_chunks = []
    current_table = []
    in_table = False

    for line in block_lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            current_table.append(line)
            in_table = True
        else:
            if in_table and current_table:
                table_chunks.append(current_table)
                current_table = []
                in_table = False

    if current_table:
        table_chunks.append(current_table)

    for table_lines in table_chunks:
        rows = parse_md_table(table_lines)
        if not rows:
            continue

        headers = list(rows[0].keys())

        # Determine table type
        has_movement = "movement" in headers
        has_weight_reps = "weight" in headers and ("reps" in headers or "sets x reps" in headers or "sets" in headers)
        has_set_col = "set" in headers
        has_duration = "duration" in headers
        has_watts_col = "watts" in headers
        has_round_col = "round" in headers

        if has_movement:
            # Case 1: Movement column table
            for row in rows:
                movement = find_col(row, ["movement"])
                if not movement or movement in ("—", "-", ""):
                    continue
                movement = strip_md_bold(movement)

                weight_str = find_col(row, ["weight", "load", "weight/intensity"])
                reps_str = find_col(row, ["reps", "sets x reps", "reps/cals", "reps/time", "output", "details"])
                notes_str = find_col(row, ["notes", "score/notes"])

                # Special: movement might be "Bench (empty bar)" etc.
                exercise = normalize_exercise(movement)

                # Skip "Total" rows
                if exercise.lower() in ("total",):
                    continue

                weight = parse_weight_lbs(weight_str or "")
                reps = parse_reps(reps_str or "")
                watts = parse_watts(weight_str or "") or parse_watts(reps_str or "")
                calories = parse_calories(reps_str or "")

                # For "sets x reps" like "4 x 12" — use reps=12, round=1
                # Already handled by parse_reps

                if weight is None and reps is None and watts is None and calories is None:
                    continue

                sets.append({
                    "exercise": exercise,
                    "round": 1,
                    "weight_lbs": weight,
                    "reps": reps,
                    "rpe": None,
                    "duration_secs": None,
                    "distance_m": None,
                    "calories": calories,
                    "watts": watts,
                    "notes": strip_md_bold(notes_str or "") or None,
                })

        elif has_set_col and ("weight" in headers
                              or any("(lbs)" in h for h in headers)
                              or any(h.endswith(" lbs") for h in headers)):
            # Case 2: Strength set table with "Set" column
            exercise_from_block = extract_exercise_from_block(block_name)

            # Named exercise columns like "bent over row (lbs)", "deadlift (lbs)"
            # Exclude generic "weight (lbs)" which is just a weight column label
            GENERIC_WEIGHT_COLS = {"weight (lbs)", "weight", "load (lbs)", "load"}
            named_exercise_cols = [
                h for h in headers
                if "(lbs)" in h and h not in GENERIC_WEIGHT_COLS
            ]
            rpe_col_list = [h for h in headers if "rpe" in h]

            # If there are named exercise columns, create sets per exercise column
            if named_exercise_cols and "weight" not in headers:
                # Superset table: each (lbs) column is a different exercise
                for row in rows:
                    set_str = find_col(row, ["set"])
                    if not set_str:
                        continue
                    set_str = strip_md_bold(set_str)
                    if set_str.lower() in ("total", "—", ""):
                        continue
                    set_nums = parse_set_range(set_str)

                    rpe_str = find_col(row, rpe_col_list + ["rpe"])
                    rpe = parse_rpe(rpe_str or "")
                    notes_str = find_col(row, ["notes"])
                    notes = strip_md_bold(notes_str or "") or None

                    # Also extract embedded RPE from notes like "×5, RPE 6-7"
                    if notes:
                        m_rpe = re.search(r"RPE\s*([\d.]+)", notes, re.IGNORECASE)
                        if m_rpe and not rpe:
                            rpe = float(m_rpe.group(1))

                    for col in named_exercise_cols:
                        col_exercise = normalize_exercise(col.replace(" (lbs)", "").strip())
                        val = strip_md_bold(row.get(col, "") or "")
                        if not val or val in ("—", "-", ""):
                            continue

                        # Reps may be embedded as "×5" in notes
                        reps = None
                        m_reps = re.search(r"[×x](\d+)", notes or "")
                        if m_reps:
                            reps = int(m_reps.group(1))

                        weight = parse_weight_lbs(val)
                        if weight is None and reps is None:
                            continue

                        for sn in set_nums:
                            sets.append({
                                "exercise": col_exercise,
                                "round": sn,
                                "weight_lbs": weight,
                                "reps": reps,
                                "rpe": rpe,
                                "duration_secs": None,
                                "distance_m": None,
                                "calories": None,
                                "watts": None,
                                "notes": notes,
                            })
            else:
                # Standard set table: use block exercise name, weight from "weight" or first named col
                weight_cols = ["weight", "weight (lbs)", "load", "load (lbs)"] + named_exercise_cols[:1]

                for row in rows:
                    set_str = find_col(row, ["set"])
                    if not set_str:
                        continue
                    set_str = strip_md_bold(set_str)
                    if set_str.lower() in ("total", "—", ""):
                        continue

                    set_nums = parse_set_range(set_str)

                    weight_str = find_col(row, weight_cols)
                    reps_str = find_col(row, ["reps", "reps/cals"])
                    rpe_str = find_col(row, rpe_col_list + ["rpe"])
                    notes_str = find_col(row, ["notes"])

                    weight = parse_weight_lbs(weight_str or "")
                    reps = parse_reps(reps_str or "")
                    rpe = parse_rpe(rpe_str or "")
                    notes = strip_md_bold(notes_str or "") or None

                    # Extract embedded reps and RPE from notes like "×5, RPE 6-7"
                    if notes and reps is None:
                        m_reps = re.search(r"[×x](\d+)", notes)
                        if m_reps:
                            reps = int(m_reps.group(1))
                    if notes and rpe is None:
                        m_rpe = re.search(r"RPE\s*([\d.]+)", notes, re.IGNORECASE)
                        if m_rpe:
                            rpe = float(m_rpe.group(1))

                    if weight is None and reps is None:
                        continue

                    for sn in set_nums:
                        sets.append({
                            "exercise": exercise_from_block,
                            "round": sn,
                            "weight_lbs": weight,
                            "reps": reps,
                            "rpe": rpe,
                            "duration_secs": None,
                            "distance_m": None,
                            "calories": None,
                            "watts": None,
                            "notes": notes,
                        })

        elif has_round_col:
            # Round-based conditioning table (e.g. rowing intervals)
            # Try to get exercise from column names (e.g. "c2 bike (cal)", "ski (cal)")
            CARDIO_KEYWORDS = ("ski", "bike", "row", "erg")
            cardio_headers = [h for h in headers if h not in ("round", "notes", "off", "total")
                              and any(kw in h for kw in CARDIO_KEYWORDS)]
            if cardio_headers:
                # Use first matching cardio column header as exercise hint
                hdr = cardio_headers[0]
                ch = None
                # Try to find a CARDIO_KEYWORD anywhere in the header
                for kw in CARDIO_KEYWORDS:
                    if kw in hdr:
                        # Extract part of header that contains the keyword
                        # e.g. "c2 bike (cal)" → "c2 bike", "cals (ski/bike)" → "ski"
                        # First try before parens
                        before_paren = re.sub(r"\s*\(.*\)", "", hdr).strip()
                        if kw in before_paren:
                            ch = re.sub(r"\s*(cal|cals|watts|w)\s*$", "", before_paren, flags=re.IGNORECASE).strip()
                        else:
                            # Try inside parens
                            paren_m = re.search(r"\(([^)]+)\)", hdr)
                            if paren_m:
                                for part in paren_m.group(1).split("/"):
                                    if kw in part.strip():
                                        ch = part.strip()
                                        break
                        if ch:
                            break
                if not ch:
                    ch = re.sub(r"\s*\([^)]*\)", "", hdr).strip()
                    ch = re.sub(r"\s*(cal|cals|watts|w)\s*$", "", ch, flags=re.IGNORECASE).strip()
                exercise = normalize_exercise(ch) if ch else extract_exercise_from_block(block_name)
            else:
                exercise = extract_exercise_from_block(block_name)
            for row in rows:
                round_str = find_col(row, ["round"])
                if not round_str or strip_md_bold(round_str).lower() in ("total", "—"):
                    continue
                round_num = parse_reps(round_str) or 1
                # Try to find watts or calories in any column
                watts = None
                calories = None
                for k, v in row.items():
                    if k == "round":
                        continue
                    w = parse_watts(v or "")
                    if w and watts is None:
                        watts = w
                    c = parse_calories(v or "")
                    if c and calories is None:
                        calories = c
                if watts is None and calories is None:
                    continue
                sets.append({
                    "exercise": exercise,
                    "round": round_num,
                    "weight_lbs": None,
                    "reps": None,
                    "rpe": None,
                    "duration_secs": None,
                    "distance_m": None,
                    "calories": calories,
                    "watts": watts,
                    "notes": None,
                })

        elif has_duration and has_watts_col:
            # Cardio/conditioning table with duration+watts columns
            exercise = extract_exercise_from_block(block_name)
            for i, row in enumerate(rows, start=1):
                duration_str = find_col(row, ["duration"])
                watts_str = find_col(row, ["watts"])
                watts = parse_watts(watts_str or "")
                if watts is None:
                    continue
                sets.append({
                    "exercise": exercise,
                    "round": i,
                    "weight_lbs": None,
                    "reps": None,
                    "rpe": None,
                    "duration_secs": None,
                    "distance_m": None,
                    "calories": None,
                    "watts": watts,
                    "notes": None,
                })

        elif "weight" in headers and ("sets" in headers or "sets x reps" in headers):
            # Table with Weight + Sets (no Set column) — like "Dips | Sets | Reps"
            exercise = extract_exercise_from_block(block_name)
            for row in rows:
                weight_str = find_col(row, ["weight"])
                sets_str = find_col(row, ["sets"])
                reps_str = find_col(row, ["reps", "sets x reps"])

                # Handle "3 x 10" in sets column — treat sets as just count
                weight = parse_weight_lbs(weight_str or "")
                reps = parse_reps(reps_str or "") or parse_reps(sets_str or "")

                if weight is None and reps is None:
                    continue

                sets.append({
                    "exercise": exercise,
                    "round": 1,
                    "weight_lbs": weight,
                    "reps": reps,
                    "rpe": None,
                    "duration_secs": None,
                    "distance_m": None,
                    "calories": None,
                    "watts": None,
                    "notes": None,
                })

        elif "weight" in headers and "reps" in headers:
            # Standard Weight+Reps table without Set column
            exercise = extract_exercise_from_block(block_name)
            for i, row in enumerate(rows, start=1):
                weight_str = find_col(row, ["weight"])
                reps_str = find_col(row, ["reps"])
                weight = parse_weight_lbs(weight_str or "")
                reps = parse_reps(reps_str or "")
                if weight is None and reps is None:
                    continue
                sets.append({
                    "exercise": exercise,
                    "round": i,
                    "weight_lbs": weight,
                    "reps": reps,
                    "rpe": None,
                    "duration_secs": None,
                    "distance_m": None,
                    "calories": None,
                    "watts": None,
                    "notes": None,
                })

        else:
            # Superset / multi-exercise tables with named columns
            # Try to parse each row generically
            exercise = extract_exercise_from_block(block_name)

            # Look for named exercise columns (e.g. "bent over row (lbs)", "kb pendlay row (lbs)")
            lbs_cols = [h for h in headers if "(lbs)" in h]
            rpe_col = [h for h in headers if "rpe" in h]

            if lbs_cols:
                for row in rows:
                    set_str = find_col(row, ["set"])
                    if set_str:
                        set_str = strip_md_bold(set_str)
                        if set_str.lower() in ("total", "—", ""):
                            continue
                    set_nums = parse_set_range(set_str or "1")

                    for col in lbs_cols:
                        # Derive exercise name from column header
                        col_exercise = col.replace(" (lbs)", "").strip()
                        col_exercise = normalize_exercise(col_exercise)

                        val = row.get(col, "")
                        val = strip_md_bold(val)

                        if not val or val in ("—", "-", ""):
                            continue

                        # Parse reps from "×5" embedded in value
                        reps = None
                        m_reps = re.search(r"[×x](\d+)", val)
                        if m_reps:
                            reps = int(m_reps.group(1))
                            val = re.sub(r",?\s*[×x]\d+.*$", "", val).strip()

                        weight = parse_weight_lbs(val)
                        rpe_str = find_col(row, rpe_col + ["rpe"])
                        rpe = parse_rpe(rpe_str or "")
                        notes_str = find_col(row, ["notes"])
                        notes = strip_md_bold(notes_str or "") or None

                        if weight is None and reps is None:
                            continue

                        for sn in set_nums:
                            sets.append({
                                "exercise": col_exercise,
                                "round": sn,
                                "weight_lbs": weight,
                                "reps": reps,
                                "rpe": rpe,
                                "duration_secs": None,
                                "distance_m": None,
                                "calories": None,
                                "watts": None,
                                "notes": notes,
                            })
            else:
                # Can't parse this table, skip
                pass

    return sets


# ──────────────────────────────────────────────────────────────────────────────
# Database operations
# ──────────────────────────────────────────────────────────────────────────────

def get_or_create_exercise(conn: sqlite3.Connection, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO exercises(name) VALUES (?)", (name,))
    row = conn.execute("SELECT id FROM exercises WHERE name = ?", (name,)).fetchone()
    return row[0]


def import_workout(conn: sqlite3.Connection, workout: dict) -> tuple[int, int, int]:
    """Import one workout. Returns (blocks_count, sets_count, exercises_created)."""
    cur = conn.execute(
        "INSERT INTO workouts(name, date, sleep_hours, tags, notes) VALUES (?, ?, ?, ?, ?)",
        (
            workout["name"],
            workout["date"],
            workout["sleep_hours"],
            json.dumps(workout["tags"]),
            workout["notes"],
        ),
    )
    workout_id = cur.lastrowid
    logged_at = f"{workout['date']} 12:00:00"

    total_blocks = 0
    total_sets = 0

    for order, block in enumerate(workout["blocks"], start=1):
        block_name = block["name"]
        block_lines = block["lines"]

        cur2 = conn.execute(
            'INSERT INTO blocks(workout_id, name, "order") VALUES (?, ?, ?)',
            (workout_id, block_name, order),
        )
        block_id = cur2.lastrowid
        total_blocks += 1

        sets = extract_sets_from_block(block_name, block_lines)

        for s in sets:
            exercise_id = get_or_create_exercise(conn, s["exercise"])
            conn.execute(
                """INSERT INTO sets(block_id, exercise_id, round, weight_lbs, reps, rpe,
                   duration_secs, distance_m, calories, watts, notes, logged_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    block_id,
                    exercise_id,
                    s["round"],
                    s["weight_lbs"],
                    s["reps"],
                    s["rpe"],
                    s["duration_secs"],
                    s["distance_m"],
                    s["calories"],
                    s["watts"],
                    s["notes"],
                    logged_at,
                ),
            )
            total_sets += 1

    return total_blocks, total_sets


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    base = Path("/Users/ayush29feb/Developement/gym/workouts")

    # Collect source files (no duplicates)
    source_dirs = [
        base / "archive" / "history",  # 2025 APS workouts
        base / "archive" / "2026",     # MPA Squad W9-W12 canonical
        base / "2026",                 # newer 2026 workouts
    ]

    files = []
    for d in source_dirs:
        md_files = sorted(d.glob("*.md"))
        files.extend(md_files)

    # Sort chronologically by filename prefix
    files.sort(key=lambda p: p.name)

    print(f"Found {len(files)} workout files to import:")
    for f in files:
        print(f"  {f.name}")
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Clear existing data
    print("Clearing existing data...")
    conn.execute("DELETE FROM sets")
    conn.execute("DELETE FROM blocks")
    conn.execute("DELETE FROM workouts")
    conn.execute("DELETE FROM exercises")
    conn.execute("DELETE FROM exercise_relations")
    # Reset auto-increment sequences (sqlite_sequence only exists if AUTOINCREMENT was used)
    try:
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('sets','blocks','workouts','exercises')")
    except sqlite3.OperationalError:
        pass
    conn.commit()

    total_workouts = 0
    total_blocks = 0
    total_sets = 0
    errors = []

    for filepath in files:
        try:
            workout = parse_workout_file(str(filepath))
            if not workout["date"]:
                print(f"  SKIP (no date): {filepath.name}")
                continue

            b, s = import_workout(conn, workout)[:2]
            total_workouts += 1
            total_blocks += b
            total_sets += s
            print(f"  ✓ {filepath.name}: {b} blocks, {s} sets")

        except Exception as e:
            errors.append((filepath.name, str(e)))
            print(f"  ✗ ERROR {filepath.name}: {e}")
            import traceback
            traceback.print_exc()

    conn.commit()

    # Count exercises
    total_exercises = conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0]

    print()
    print("=" * 60)
    print(f"Import complete:")
    print(f"  Workouts  : {total_workouts}")
    print(f"  Exercises : {total_exercises}")
    print(f"  Blocks    : {total_blocks}")
    print(f"  Sets      : {total_sets}")
    if errors:
        print(f"  Errors    : {len(errors)}")
        for name, err in errors:
            print(f"    {name}: {err}")

    conn.close()


if __name__ == "__main__":
    main()
