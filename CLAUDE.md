# AC Logs — Claude Operating Guide

## First-Time Setup

Use this guide when a user asks to set up AC Logs. Walk them through steps in order. **Never ask the user to run commands — always ask for permission and run them yourself.**

**Trigger phrases:**
- "first time" → skip Step 2
- "again" / "new machine" → include Step 2

### Step 1 — Install dependencies

Ask: "Can I run the setup script to install dependencies and initialize the project?"

Once confirmed:
```bash
./setup.sh
```

This installs all Node dependencies, builds the server, generates the Prisma client, generates Relay types, and creates `server/.env` with the correct database path.

Tell the user: **Dependencies installed.**

---

### Step 2 — Restore backup data (re-setup only)

Ask: "Do you have a backup `data/` directory to restore? If so, where is it?"

- **No**: continue.
- **Yes**: ask for the path, then ask permission to copy:

```bash
GYM=$(git rev-parse --show-toplevel)
cp -r /path/to/backup/data/. "$GYM/data/"
```

Verify:
```bash
ls "$GYM/data/"
```

Tell the user: **Backup data restored.**

---

### Step 3 — Start the servers

Check for existing processes first:
```bash
lsof -ti :47322 -ti :47323
```

If PIDs are returned, ask: "There are already processes running on AC Logs' ports — likely a previous session. Can I kill them and start fresh?" After confirmation:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Then ask: "Can I start the GraphQL server and dashboard?" Once confirmed:
```bash
GYM=$(git rev-parse --show-toplevel)
cd "$GYM/server" && npm start &> /tmp/gym-server.log &
cd "$GYM/dashboard" && npm run dev -- --host &> /tmp/gym-dashboard.log &
sleep 3 && lsof -i :47322 -i :47323 | grep LISTEN
```

Tell the user: **Both servers are running.**
- GraphQL server: `http://localhost:47322/graphql`
- Dashboard: `http://localhost:47323` (also on phone via Tailscale)

---

### Step 4 — Set up Tailscale (dashboard on phone)

> To open the dashboard on your phone, you need Tailscale — a free tool that creates a private connection between your Mac and phone.
>
> **On your Mac:** Go to tailscale.com/download, install, launch, and sign in.
> **On your phone:** Install Tailscale from the App Store/Play Store, sign in with the same account.
>
> Once both devices are connected, let me know and I'll give you the URL.

Once confirmed:
```bash
tailscale ip -4
```

Tell the user: open `http://<ip>:47323` in your phone's browser and bookmark it.

---

### Step 5 — Done

**AC Logs is ready.** Ongoing:
- Open the Tailscale URL on your phone to view the dashboard
- Say "start the servers" anytime to restart
- The date range picker (top-right) filters both History and PRs simultaneously

---

## Key Paths

All paths relative to repo root (`git rev-parse --show-toplevel`).

| Resource | Path |
|---|---|
| Database | `data/gym.db` |
| Workouts (markdown source) | `workouts/` |
| Import script | `cli/import_workouts.py` |
| Server | `server/` |
| Dashboard | `dashboard/` |
| Server env | `server/.env` |

---

## Running the Servers

**Never ask the user to run commands — always ask for permission and run yourself.**

Kill existing:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Start both:
```bash
GYM=$(git rev-parse --show-toplevel)
cd "$GYM/server" && npm start &> /tmp/gym-server.log &
cd "$GYM/dashboard" && npm run dev -- --host &> /tmp/gym-dashboard.log &
sleep 2 && lsof -i :47322 -i :47323 | grep LISTEN
```

Check if running:
```bash
lsof -i :47322 -i :47323 | grep LISTEN
```

View logs:
```bash
tail -f /tmp/gym-server.log
tail -f /tmp/gym-dashboard.log
```

Kill servers:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Start from phone (user types `!` prefix in chat):
```
! lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
! GYM=$(git rev-parse --show-toplevel) && cd "$GYM/server" && npm start &> /tmp/gym-server.log &
! GYM=$(git rev-parse --show-toplevel) && cd "$GYM/dashboard" && npm run dev -- --host &> /tmp/gym-dashboard.log &
```

---

## Common Problems & Fixes

### Server starts but returns no data

Check `server/.env` — `DATABASE_URL` must be an absolute path: `file:///absolute/path/to/data/gym.db`. A relative path silently creates a new empty DB.

### Dashboard blank screen

Usually a JS error. Check browser console. Common causes:
- Relay types out of date: `cd dashboard && npm run relay`
- GraphQL field missing from `dashboard/schema.graphql` — add it then run `npm run relay`

### `prisma generate` needed

If the Prisma schema changed:
```bash
GYM=$(git rev-parse --show-toplevel)
cd "$GYM/server" && npx prisma generate && npm run build
```

### Port already in use
```bash
lsof -i :47322 -i :47323 | grep LISTEN
kill -9 <PID>
```

### No data in DB

The database must be seeded from the workout markdown files:
```bash
GYM=$(git rev-parse --show-toplevel)
cd "$GYM/cli" && uv run python import_workouts.py
```

---

## Markdown Files

| File | Purpose |
|---|---|
| `README.md` | Project overview for new users — short, non-technical |
| `CONTRIBUTING.md` | Technical reference: architecture, schema, dev setup |
| `CLAUDE.md` | This file — operating guide for Claude |
