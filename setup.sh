#!/usr/bin/env bash
set -euo pipefail

GYM="$(cd "$(dirname "$0")" && pwd)"
echo "Setting up AC Logs at: $GYM"

# ── Node server ──────────────────────────────────────────────────────
echo "Installing server dependencies..."
cd "$GYM/server" && npm install && npm run build

# ── Prisma client ────────────────────────────────────────────────────
echo "Generating Prisma client..."
cd "$GYM/server" && npx prisma generate

# ── Dashboard ────────────────────────────────────────────────────────
echo "Installing dashboard dependencies..."
cd "$GYM/dashboard" && npm install

# ── server/.env ──────────────────────────────────────────────────────
ENV_FILE="$GYM/server/.env"
mkdir -p "$GYM/data"
if [ ! -f "$ENV_FILE" ]; then
  echo "Creating server/.env..."
  echo "DATABASE_URL=\"file://$GYM/data/gym.db\"" > "$ENV_FILE"
fi

# ── Relay types ──────────────────────────────────────────────────────
echo "Generating Relay types..."
cd "$GYM/dashboard" && npm run relay

# ── Verify DB ────────────────────────────────────────────────────────
DB_FILE="$GYM/data/gym.db"
if [ ! -f "$DB_FILE" ]; then
  echo ""
  echo "⚠  No database found at $DB_FILE"
  echo "   Run the migration script to populate your workout data:"
  echo "   cd $GYM/cli && uv run python import_workouts.py"
  echo ""
else
  TABLES=$(sqlite3 "$DB_FILE" ".tables" 2>/dev/null || true)
  for TABLE in workouts blocks sets exercises; do
    if ! echo "$TABLES" | grep -qw "$TABLE"; then
      echo "✗ Missing table '$TABLE' in $DB_FILE"
      exit 1
    fi
  done
  echo "✓ Database verified."
fi

# ── Shell profile ────────────────────────────────────────────────────
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
  SHELL_RC="$HOME/.bash_profile"
fi

if [ -n "$SHELL_RC" ]; then
  if grep -q 'export GYM=' "$SHELL_RC"; then
    sed -i '' "s|export GYM=.*|export GYM=\"$GYM\"|" "$SHELL_RC"
  else
    echo "export GYM=\"$GYM\"" >> "$SHELL_RC"
  fi
  echo "Added GYM=$GYM to $SHELL_RC"
fi

echo ""
echo "✓ AC Logs is ready."
echo ""
echo "Next: open Claude Code in this directory and say 'start the servers'"
