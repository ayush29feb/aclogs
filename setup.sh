#!/usr/bin/env bash
set -e

GYM_ROOT="$(git rev-parse --show-toplevel)"
echo "Setting up gym at $GYM_ROOT"

# Install CLI
cd "$GYM_ROOT/cli"
uv sync

# Create data dir
mkdir -p "$GYM_ROOT/data"

echo ""
echo "Setup complete. Add this to your shell profile:"
echo "  export GYM=$GYM_ROOT"
echo "  alias gym='$GYM_ROOT/cli/.venv/bin/gym'"
