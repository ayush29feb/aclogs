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
