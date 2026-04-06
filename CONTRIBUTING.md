# AC Logs — Technical Reference

## Architecture

```
gym/
├── cli/          # Python import scripts — populate the database
├── server/       # Node.js GraphQL server — reads DB, serves API
├── dashboard/    # React/Relay SPA — visualization
├── workouts/     # Source workout markdown files
└── data/         # SQLite database (gitignored)
    └── gym.db
```

### How the pieces connect

```
CLI (Python)
    └── writes → data/gym.db

GraphQL Server (Node.js / Prisma + graphql-yoga)
    ├── reads  → data/gym.db  (via DATABASE_URL env var)
    └── serves → POST /graphql

Dashboard (React / Relay / Vite)
    └── queries → /graphql  (proxied to localhost:47322 by Vite)
```

---

## Database Schema

Five tables in `data/gym.db`:

| Table | Purpose |
|---|---|
| `workouts` | Training sessions with date, name, tags, sleep, notes |
| `blocks` | Named sections within a workout (e.g. "Main", "Accessories") |
| `sets` | Individual sets: exercise, reps, weight, RPE, duration, etc. |
| `exercises` | Exercise catalog with muscle group |
| `exercise_relations` | Links between related exercises (e.g. squat ↔ pause squat) |

**Blocks** belong to workouts. **Sets** belong to blocks and reference an exercise. Rounds are derived from the `round` integer column on sets.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Import CLI | Python 3.11+, uv |
| Server | Node.js, TypeScript, graphql-yoga, Prisma 5 |
| Dashboard | React 18, Relay, Vite, React Router, TypeScript |
| Database | SQLite (single file) |

---

## Setup

### Prerequisites

- Node.js 20+
- npm

### First time

```bash
./setup.sh
```

This installs all dependencies, builds the server, generates the Prisma client, creates `server/.env`, and generates Relay types.

### Manual steps

```bash
# Server
cd server && npm install && npm run build && npx prisma generate

# Dashboard
cd dashboard && npm install && npm run relay

# .env (if not created by setup.sh)
echo 'DATABASE_URL="file:///absolute/path/to/data/gym.db"' > server/.env
```

---

## Running

### Development

Start GraphQL server (port 47322):
```bash
cd server
npm run dev     # tsx watch — auto-restarts on changes
npm start       # runs compiled dist/index.js
```

Start dashboard (port 47323):
```bash
cd dashboard
npm run dev                  # localhost only
npm run dev -- --host        # bind all interfaces (for Tailscale)
```

Vite proxies `/graphql` to `http://localhost:47322`.

### After schema changes

If you modify `server/src/schema.ts` or `dashboard/schema.graphql`:
```bash
cd dashboard && npm run relay
```

If you modify `server/prisma/schema.prisma`:
```bash
cd server && npx prisma generate
```

---

## Dashboard Views

| View | Route | Description |
|---|---|---|
| History | `/history` | Workout sessions — expandable cards with blocks and sets. Tag filter (multi-select intersection). Session count shown. |
| PRs | `/progress` | Best weight per rep count (1/3/5/8 RM) per exercise. Workout count column. Click row for sparkline. |

Global date range picker (top-right of topbar) filters both views.

---

## Importing Workouts

Workout sessions are stored as markdown files in `workouts/`. The import script reads these and populates the database.

```bash
cd cli
uv run python import_workouts.py
```

This wipes existing data and re-imports from scratch. The script is hardcoded per-workout to ensure correct rep schemes and weights.

---

## Updating Landing Page Screenshots

The `docs/index.html` landing page uses real screenshots from the running app. Regenerate them when the UI changes.

### Prerequisites

Both servers must be running (ports 47322 and 47323). Then:

```bash
mkdir -p /tmp/gym-pw && cd /tmp/gym-pw
npm init -y && npm install playwright
npx playwright install chromium
```

### Capture script

```bash
cat > /tmp/gym-pw/capture.mjs << 'EOF'
import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import path from 'path';

const GYM = process.env.GYM;
if (!GYM) throw new Error('GYM env not set');
const OUT = path.join(GYM, 'docs/images');
await mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
});
const page = await context.newPage();

async function capture(route, name) {
  await page.goto(`http://localhost:47323${route}`, { waitUntil: 'networkidle', timeout: 20000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(OUT, `${name}.jpg`), type: 'jpeg', quality: 92 });
  console.log(`✓ ${name}.jpg`);
}

await capture('/history', 'history');
await capture('/progress', 'prs');
await browser.close();
EOF
```

### Run

```bash
GYM=$(git rev-parse --show-toplevel) node /tmp/gym-pw/capture.mjs
```

### Commit

```bash
cd "$(git rev-parse --show-toplevel)"
git add docs/images/
git commit -m "docs: refresh landing page screenshots"
git push
```

---

## Common Problems

### Server returns no data

Check `server/.env` — `DATABASE_URL` must use an absolute path: `file:///absolute/path/to/data/gym.db`.

### Dashboard blank / JS error

Relay types may be out of date:
```bash
cd dashboard && npm run relay
```

### Port already in use
```bash
lsof -i :47322 -i :47323 | grep LISTEN
kill -9 <PID>
```

### Prisma type errors after schema change
```bash
cd server && npx prisma generate && npm run build
```
