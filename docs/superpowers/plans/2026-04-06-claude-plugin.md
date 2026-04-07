# AC Logs Claude Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the AC Logs repo into an installable Claude Code plugin so `claude plugin install ayush29feb/aclogs` installs the full app (server, dashboard, CLI) plus Claude skills for setup, server management, workout import, and remote access.

**Architecture:** Plugin metadata and skill files are added alongside the existing app code — nothing moves except the database, which migrates to `~/.aclogs/data/gym.db` so it persists across plugin updates. A session-start hook injects the plugin root path and skill awareness into Claude's context. Skills replace the existing CLAUDE.md operating guide with discrete, invokable instructions.

**Tech Stack:** Bash (hooks, setup script), Markdown (skills), JSON (hooks.json, package.json), existing Node.js/Python/SQLite stack unchanged.

---

## File Map

| Action | File | Purpose |
|---|---|---|
| Create | `package.json` | Plugin metadata (name, version) |
| Modify | `setup.sh` | Write data to `~/.aclogs/data/`, write `~/.aclogs/config` |
| Create | `hooks/hooks.json` | Register session-start hook |
| Create | `hooks/session-start` | Inject plugin root + skill list into Claude context |
| Create | `skills/setup.md` | First-time and re-setup skill |
| Create | `skills/start-servers.md` | Start GraphQL server + dashboard skill |
| Create | `skills/stop-servers.md` | Stop both servers skill |
| Create | `skills/import-workouts.md` | Run CLI import skill |
| Create | `skills/remote-control.md` | Tailscale setup + phone URL skill |
| Modify | `CLAUDE.md` | Lightweight: tells Claude to use skills |

---

## Task 1: Plugin metadata

**Files:**
- Create: `package.json`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "aclogs",
  "version": "1.0.0",
  "description": "AC Logs — self-hosted workout tracker for Athletic Clubs members"
}
```

- [ ] **Step 2: Verify it's valid JSON**

```bash
node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add package.json
git commit -m "plugin: add package.json metadata"
```

---

## Task 2: Update setup.sh for data persistence

**Files:**
- Modify: `setup.sh`

The database must live outside the plugin directory so plugin updates don't wipe it. `setup.sh` currently writes `data/gym.db` relative to the repo. Change it to write `~/.aclogs/data/gym.db`. Also write `~/.aclogs/config` so skills can find the plugin root path.

- [ ] **Step 1: Replace the data dir section**

Current (lines around `mkdir -p "$GYM/data"`):
```bash
ENV_FILE="$GYM/server/.env"
mkdir -p "$GYM/data"
if [ ! -f "$ENV_FILE" ]; then
  echo "Creating server/.env..."
  echo "DATABASE_URL=\"file://$GYM/data/gym.db\"" > "$ENV_FILE"
fi
```

Replace with:
```bash
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
```

- [ ] **Step 2: Update the DB verify section**

Current:
```bash
DB_FILE="$GYM/data/gym.db"
```

Replace with:
```bash
DB_FILE="$DATA_DIR/gym.db"
```

- [ ] **Step 3: Remove the shell profile section**

The plugin install path is not predictable enough to export as `GYM=`. Remove this block entirely (from `# ── Shell profile ──` to the final `fi`):

```bash
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
```

- [ ] **Step 4: Update final message**

Current:
```bash
echo "Next: open Claude Code in this directory and say 'start the servers'"
```

Replace with:
```bash
echo "Next: in any Claude Code session, say 'start AC Logs servers'"
```

- [ ] **Step 5: Verify setup.sh runs without error**

```bash
bash -n setup.sh && echo "syntax ok"
```

Expected: `syntax ok`

- [ ] **Step 6: Commit**

```bash
git add setup.sh
git commit -m "plugin: update setup.sh to write data to ~/.aclogs/"
```

---

## Task 3: Session-start hook

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/session-start`

The hook fires at session start and injects a short context message telling Claude that AC Logs is installed and which skills are available. It reads `~/.aclogs/config` to get the plugin root path.

- [ ] **Step 1: Create hooks/hooks.json**

```bash
mkdir -p hooks
```

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Create hooks/session-start**

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG="$HOME/.aclogs/config"

# Only inject context if AC Logs has been set up
if [ ! -f "$CONFIG" ]; then
  exit 0
fi

source "$CONFIG"

escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

context="AC Logs is installed at ${ACLOGS_ROOT}. Database is at ${ACLOGS_DATA}/gym.db. If the user asks about their workouts, AC Logs, lifting data, or wants to start/stop servers, use the AC Logs skills: aclogs:setup, aclogs:start-servers, aclogs:stop-servers, aclogs:import-workouts, aclogs:remote-control."

escaped=$(escape_for_json "$context")

if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -z "${COPILOT_CLI:-}" ]; then
  printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "$escaped"
else
  printf '{\n  "additionalContext": "%s"\n}\n' "$escaped"
fi

exit 0
```

- [ ] **Step 3: Make session-start executable**

```bash
chmod +x hooks/session-start
```

- [ ] **Step 4: Verify the script runs and produces valid JSON**

```bash
CLAUDE_PLUGIN_ROOT="$(pwd)" bash hooks/session-start | python3 -m json.tool
```

Expected: JSON prints without error. If `~/.aclogs/config` doesn't exist yet, the script exits 0 with no output (that's correct — skip the test of the JSON branch until after setup.sh has been run).

- [ ] **Step 5: Commit**

```bash
git add hooks/
git commit -m "plugin: add session-start hook"
```

---

## Task 4: setup skill

**Files:**
- Create: `skills/setup.md`

This skill replaces Steps 1–5 of the existing CLAUDE.md. It references `~/.aclogs/config` for paths and `$ACLOGS_ROOT/setup.sh` for the install script.

- [ ] **Step 1: Create skills/setup.md**

```bash
mkdir -p skills
```

````markdown
---
name: setup
description: Use when the user asks to set up AC Logs for the first time, or set it up again on a new machine
---

# AC Logs Setup

Walk the user through setup in order. Never ask the user to run commands — always ask permission and run yourself.

**Trigger phrases:**
- "first time" → skip Step 2
- "again" / "new machine" → include Step 2

## Step 1 — Install dependencies

Ask: "Can I run the setup script to install dependencies and initialize AC Logs?"

Once confirmed, find the plugin root:
```bash
source ~/.aclogs/config 2>/dev/null || ACLOGS_ROOT="${CLAUDE_PLUGIN_ROOT}"
```

Then run:
```bash
bash "$ACLOGS_ROOT/setup.sh"
```

This installs all Node dependencies, builds the server, generates the Prisma client, generates Relay types, creates `~/.aclogs/data/`, and writes `server/.env` with the correct database path.

Tell the user: **Dependencies installed.**

---

## Step 2 — Restore backup data (re-setup only)

Ask: "Do you have a backup of your workout database to restore? If so, where is it?"

- **No**: continue.
- **Yes**: ask for the path to the backup `gym.db` file, then ask permission to copy:

```bash
cp /path/to/backup/gym.db "$HOME/.aclogs/data/gym.db"
```

Verify:
```bash
ls -lh "$HOME/.aclogs/data/gym.db"
```

Tell the user: **Backup data restored.**

---

## Step 3 — Start the servers

Use the aclogs:start-servers skill.

---

## Step 4 — Remote access on phone (optional)

Use the aclogs:remote-control skill.

---

## Step 5 — Done

**AC Logs is ready.**
- Dashboard: `http://localhost:47323`
- Say "start AC Logs servers" any time to restart
- The date range picker (top-right) filters both History and PRs simultaneously
````

- [ ] **Step 2: Verify file exists and has frontmatter**

```bash
head -5 skills/setup.md
```

Expected: first line is `---`, third line starts with `name: setup`.

- [ ] **Step 3: Commit**

```bash
git add skills/setup.md
git commit -m "plugin: add setup skill"
```

---

## Task 5: start-servers skill

**Files:**
- Create: `skills/start-servers.md`

- [ ] **Step 1: Create skills/start-servers.md**

````markdown
---
name: start-servers
description: Use when the user asks to start AC Logs, start the servers, or open the dashboard
---

# Start AC Logs Servers

Never ask the user to run commands — always ask permission and run yourself.

Ask: "Can I start the AC Logs servers?"

Once confirmed:

```bash
source ~/.aclogs/config
```

Check for existing processes:
```bash
lsof -ti :47322 -ti :47323
```

If PIDs are returned, ask: "There are already processes running on AC Logs' ports — likely a previous session. Can I kill them and start fresh?" After confirmation:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Start both servers:
```bash
cd "$ACLOGS_ROOT/server" && npm start &> /tmp/aclogs-server.log &
cd "$ACLOGS_ROOT/dashboard" && npm run dev -- --host &> /tmp/aclogs-dashboard.log &
sleep 3 && lsof -i :47322 -i :47323 | grep LISTEN
```

Tell the user: **Both servers are running.**
- GraphQL server: `http://localhost:47322/graphql`
- Dashboard: `http://localhost:47323` (also accessible on phone via Tailscale — use the aclogs:remote-control skill for the phone URL)

## View logs

```bash
tail -f /tmp/aclogs-server.log
tail -f /tmp/aclogs-dashboard.log
```
````

- [ ] **Step 2: Commit**

```bash
git add skills/start-servers.md
git commit -m "plugin: add start-servers skill"
```

---

## Task 6: stop-servers skill

**Files:**
- Create: `skills/stop-servers.md`

- [ ] **Step 1: Create skills/stop-servers.md**

````markdown
---
name: stop-servers
description: Use when the user asks to stop AC Logs or shut down the servers
---

# Stop AC Logs Servers

Ask: "Can I stop the AC Logs servers?"

Once confirmed:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Verify both ports are clear:
```bash
lsof -i :47322 -i :47323 | grep LISTEN || echo "Servers stopped."
```

Tell the user: **Servers stopped.**
````

- [ ] **Step 2: Commit**

```bash
git add skills/stop-servers.md
git commit -m "plugin: add stop-servers skill"
```

---

## Task 7: import-workouts skill

**Files:**
- Create: `skills/import-workouts.md`

- [ ] **Step 1: Create skills/import-workouts.md**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add skills/import-workouts.md
git commit -m "plugin: add import-workouts skill"
```

---

## Task 8: remote-control skill

**Files:**
- Create: `skills/remote-control.md`

- [ ] **Step 1: Create skills/remote-control.md**

````markdown
---
name: remote-control
description: Use when the user asks to access the dashboard on their phone, set up remote access, or get the Tailscale URL
---

# Remote Control — Dashboard on Phone

AC Logs can be opened on your phone over Tailscale, a free tool that creates a private connection between your Mac and phone.

## If Tailscale is not installed

Tell the user:
> **On your Mac:** Go to tailscale.com/download, install, launch, and sign in.
> **On your phone:** Install Tailscale from the App Store or Play Store and sign in with the same account.
> Once both devices show as connected in the Tailscale app, let me know.

## Once Tailscale is running on both devices

Get the Mac's Tailscale IP:
```bash
tailscale ip -4
```

Tell the user: open `http://<ip>:47323` in your phone's browser and bookmark it.

Make sure the dashboard server is running with `--host` (the aclogs:start-servers skill does this automatically).
````

- [ ] **Step 2: Commit**

```bash
git add skills/remote-control.md
git commit -m "plugin: add remote-control skill"
```

---

## Task 9: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

Replace the full operating guide with a short context-setter. The detailed instructions now live in skills.

- [ ] **Step 1: Replace CLAUDE.md content**

```markdown
# AC Logs

AC Logs is a self-hosted workout tracker for Athletic Clubs members. It runs a GraphQL server (port 47322) and a React dashboard (port 47323).

When the user asks about workouts, lifting data, or server management, use the AC Logs skills:

- **aclogs:setup** — first-time setup or re-setup on a new machine
- **aclogs:start-servers** — start the GraphQL server and dashboard
- **aclogs:stop-servers** — stop the servers
- **aclogs:import-workouts** — wipe and re-import workout data from markdown files
- **aclogs:remote-control** — set up Tailscale and get the phone URL

Data lives at `~/.aclogs/data/gym.db`. Plugin root is in `~/.aclogs/config`.
```

- [ ] **Step 2: Verify**

```bash
wc -l CLAUDE.md
```

Expected: under 20 lines.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "plugin: replace CLAUDE.md with lightweight skill pointer"
```

---

## Task 10: End-to-end verification

- [ ] **Step 1: Verify directory structure**

```bash
find . -path ./node_modules -prune -o -path ./.git -prune -o \
  -name "*.json" -print -o -name "*.md" -print -o -name "session-start" -print \
  | grep -E "^\./(package\.json|hooks/|skills/|CLAUDE\.md)" | sort
```

Expected output:
```
./CLAUDE.md
./hooks/hooks.json
./hooks/session-start
./skills/import-workouts.md
./skills/remote-control.md
./skills/setup.md
./skills/start-servers.md
./skills/stop-servers.md
./package.json
```

- [ ] **Step 2: Verify hooks.json is valid JSON**

```bash
node -e "JSON.parse(require('fs').readFileSync('hooks/hooks.json','utf8')); console.log('valid')"
```

Expected: `valid`

- [ ] **Step 3: Verify all skills have valid frontmatter**

```bash
for f in skills/*.md; do
  name=$(grep '^name:' "$f" | head -1)
  desc=$(grep '^description:' "$f" | head -1)
  echo "$f: $name | $desc"
done
```

Expected: each file prints a non-empty name and description.

- [ ] **Step 4: Verify session-start script syntax**

```bash
bash -n hooks/session-start && echo "syntax ok"
```

Expected: `syntax ok`

- [ ] **Step 5: Verify setup.sh syntax**

```bash
bash -n setup.sh && echo "syntax ok"
```

Expected: `syntax ok`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "plugin: verified end-to-end structure" --allow-empty
git push
```
