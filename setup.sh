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
DATA_DIR="$HOME/.aclogs/data"
CONFIG_FILE="$HOME/.aclogs/config"
ENV_FILE="$GYM/server/.env"

mkdir -p "$DATA_DIR"

# Write config so skills can locate the plugin root
cat > "$CONFIG_FILE" << EOF
ACLOGS_ROOT="$GYM"
ACLOGS_DATA="$DATA_DIR"
EOF

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating server/.env..."
  echo "DATABASE_URL=\"file://$DATA_DIR/gym.db\"" > "$ENV_FILE"
fi

# ── Relay types ──────────────────────────────────────────────────────
echo "Generating Relay types..."
cd "$GYM/dashboard" && npm run relay

# ── Verify DB ────────────────────────────────────────────────────────
DB_FILE="$DATA_DIR/gym.db"
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

echo ""
echo "✓ AC Logs is ready."
echo ""
echo "Next: in any Claude Code session, say 'start AC Logs servers'"
