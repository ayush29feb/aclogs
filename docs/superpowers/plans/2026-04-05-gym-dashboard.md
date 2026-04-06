# Gym Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-first React/Relay dashboard with two views — workout History (expandable list with tag filter) and Progress (PR table + weight-over-time chart for any exercise).

**Architecture:** React 18 + Relay 16 + Vite on port 47323, proxying `/graphql` to the gym server at port 47322. Relay compiler generates TypeScript types from a local `schema.graphql`. Two views: HistoryView and ProgressView, each using `useLazyLoadQuery`. CSS variables + bottom nav, same design language as khana.

**Tech Stack:** React 18, Relay 16, react-relay, relay-compiler, Vite 5, vite-plugin-relay, TypeScript 5, react-router-dom 6. No charting library — weight-over-time chart is a custom SVG.

---

## File Structure

| File | Purpose |
|------|---------|
| `dashboard/package.json` | npm config, scripts, deps |
| `dashboard/tsconfig.json` | TypeScript config |
| `dashboard/vite.config.ts` | Vite + relay plugin, port 47323, proxy to 47322 |
| `dashboard/relay.config.json` | Relay compiler config pointing to schema.graphql |
| `dashboard/schema.graphql` | GraphQL schema (hand-written from server/src/schema.ts) |
| `dashboard/index.html` | Vite HTML entry |
| `dashboard/src/main.tsx` | React + Relay provider entry |
| `dashboard/src/RelayEnvironment.ts` | Relay environment singleton |
| `dashboard/src/index.css` | CSS variables + base styles + shell layout |
| `dashboard/src/App.tsx` | App shell: topbar, bottom nav, routes |
| `dashboard/src/views/HistoryView.tsx` | Workouts list with tag filter + expandable blocks |
| `dashboard/src/views/ProgressView.tsx` | Exercise picker + PR table + SVG sparkline |

---

### Task 1: Project scaffolding

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/tsconfig.json`
- Create: `dashboard/vite.config.ts`
- Create: `dashboard/relay.config.json`
- Create: `dashboard/index.html`
- Create: `dashboard/.gitignore`

- [ ] **Step 1: Create dashboard/package.json**

```json
{
  "name": "gym-dashboard",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "relay-compiler && tsc && vite build",
    "relay": "relay-compiler",
    "relay:watch": "relay-compiler --watch"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-relay": "^16.2.0",
    "react-router-dom": "^6.24.0",
    "relay-runtime": "^16.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/react-relay": "^13.0.3",
    "@vitejs/plugin-react": "^4.3.0",
    "relay-compiler": "^16.2.0",
    "typescript": "^5.5.0",
    "vite": "^5.3.0",
    "vite-plugin-relay": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create dashboard/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create dashboard/vite.config.ts**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import relay from 'vite-plugin-relay';

export default defineConfig({
  plugins: [react(), relay],
  server: {
    port: 47323,
    proxy: {
      '/graphql': 'http://localhost:47322',
    },
  },
});
```

- [ ] **Step 4: Create dashboard/relay.config.json**

```json
{
  "src": "./src",
  "schema": "./schema.graphql",
  "exclude": ["**/__generated__/**"],
  "language": "typescript",
  "eagerEsModules": true
}
```

- [ ] **Step 5: Create dashboard/index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Gym</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create dashboard/.gitignore**

```
node_modules/
dist/
src/**/__generated__/
```

- [ ] **Step 7: Install dependencies**

```bash
cd dashboard && npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 8: Commit**

```bash
git add dashboard/package.json dashboard/tsconfig.json dashboard/vite.config.ts dashboard/relay.config.json dashboard/index.html dashboard/.gitignore dashboard/package-lock.json
git commit -m "chore: scaffold gym dashboard project"
```

---

### Task 2: GraphQL schema file

**Files:**
- Create: `dashboard/schema.graphql`

The relay compiler needs a local `schema.graphql` that matches what the server serves. This must be written by hand from `server/src/schema.ts`.

- [ ] **Step 1: Create dashboard/schema.graphql**

```graphql
type Query {
  workouts(limit: Int, tag: String): [Workout!]!
  workout(id: Int!): Workout
  exercises: [Exercise!]!
  exercise(name: String!): Exercise
  progress(exerciseName: String!, related: Boolean): Progress!
}

type Workout {
  id: Int!
  name: String!
  date: String!
  sleepHours: Float
  tags: [String!]!
  notes: String
  blocks: [Block!]!
}

type Block {
  id: Int!
  name: String!
  order: Int!
  scheme: String
  rounds: [Round!]!
}

type Round {
  round: Int!
  sets: [Set!]!
}

type Set {
  id: Int!
  exerciseId: Int!
  exerciseName: String!
  round: Int!
  weightLbs: Float
  reps: Int
  rpe: Float
  durationSecs: Int
  distanceM: Float
  calories: Float
  watts: Float
  notes: String
  loggedAt: String!
}

type Exercise {
  id: Int!
  name: String!
  muscleGroup: String
  notes: String
  relatedExercises: [Exercise!]!
}

type Progress {
  exerciseName: String!
  prs: [RepsPr!]!
  history: [HistoryEntry!]!
}

type RepsPr {
  reps: Int!
  weightLbs: Float!
  date: String!
}

type HistoryEntry {
  date: String!
  exerciseName: String!
  weightLbs: Float
  reps: Int
  rpe: Float
  watts: Float
  calories: Float
  durationSecs: Int
}
```

- [ ] **Step 2: Commit**

```bash
git add dashboard/schema.graphql
git commit -m "feat: add GraphQL schema for relay compiler"
```

---

### Task 3: Relay environment + base styles + entry

**Files:**
- Create: `dashboard/src/RelayEnvironment.ts`
- Create: `dashboard/src/index.css`
- Create: `dashboard/src/main.tsx`

- [ ] **Step 1: Create dashboard/src/RelayEnvironment.ts**

```typescript
import { Environment, Network, RecordSource, Store, FetchFunction } from 'relay-runtime';

const fetchFn: FetchFunction = async (request, variables) => {
  const response = await fetch('/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: request.text, variables }),
  });
  return response.json();
};

const environment = new Environment({
  network: Network.create(fetchFn),
  store: new Store(new RecordSource()),
});

export default environment;
```

- [ ] **Step 2: Create dashboard/src/index.css**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #f1f5f9;
  --card: #ffffff;
  --border: #e2e8f0;
  --border-light: #f1f5f9;
  --text-1: #0f172a;
  --text-2: #475569;
  --text-3: #94a3b8;
  --accent: #6366f1;
  --accent-bg: #eef2ff;
  --green: #10b981;
  --green-bg: #d1fae5;
  --shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 6px rgba(0,0,0,.05), 0 2px 4px rgba(0,0,0,.04);
  --radius: 12px;
  --radius-sm: 6px;
}

html { -webkit-text-size-adjust: 100%; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text-1);
  line-height: 1.5;
  min-height: 100dvh;
}

h1, h2, h3 { font-weight: 600; line-height: 1.25; }

.shell {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 80px;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
}

.topbar-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  gap: 12px;
}

.topbar-brand {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.3px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  justify-content: center;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(8px);
  border-top: 1px solid var(--border);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.bottom-nav a {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 28px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-3);
  text-decoration: none;
  transition: color 0.15s;
}

.bottom-nav a.active { color: var(--accent); }

.nav-icon { font-size: 20px; }

.card {
  background: var(--card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  background: var(--accent-bg);
  color: var(--accent);
}

.tag-btn {
  padding: 4px 12px;
  border-radius: 99px;
  border: 1.5px solid var(--border);
  font-size: 12px;
  font-weight: 600;
  background: var(--card);
  color: var(--text-2);
  cursor: pointer;
  transition: all 0.15s;
}

.tag-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}
```

- [ ] **Step 3: Create dashboard/src/main.tsx**

```tsx
import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { RelayEnvironmentProvider } from 'react-relay';
import environment from './RelayEnvironment.js';
import App from './App.js';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RelayEnvironmentProvider environment={environment}>
      <BrowserRouter>
        <Suspense fallback={<p style={{ textAlign: 'center', marginTop: 48, color: 'var(--text-3)' }}>Loading…</p>}>
          <App />
        </Suspense>
      </BrowserRouter>
    </RelayEnvironmentProvider>
  </StrictMode>
);
```

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/RelayEnvironment.ts dashboard/src/index.css dashboard/src/main.tsx
git commit -m "feat: add relay environment, base styles, and entry point"
```

---

### Task 4: App shell

**Files:**
- Create: `dashboard/src/App.tsx`

- [ ] **Step 1: Create dashboard/src/App.tsx**

```tsx
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Suspense } from 'react';
import HistoryView from './views/HistoryView.js';
import ProgressView from './views/ProgressView.js';

const NAV = [
  { to: '/history',  icon: '📋', label: 'History'  },
  { to: '/progress', icon: '📈', label: 'Progress' },
];

export default function App() {
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <span className="topbar-brand">💪 Gym</span>
        </div>
      </header>

      <main className="shell">
        <Suspense fallback={<p style={{ color: 'var(--text-3)', marginTop: 32, textAlign: 'center' }}>Loading…</p>}>
          <Routes>
            <Route path="/" element={<Navigate to="/history" replace />} />
            <Route path="/history"  element={<HistoryView />} />
            <Route path="/progress" element={<ProgressView />} />
          </Routes>
        </Suspense>
      </main>

      <nav className="bottom-nav">
        {NAV.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'active' : ''}>
            <span className="nav-icon">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
```

- [ ] **Step 2: Run relay compiler to generate types**

The relay compiler needs at least one `graphql` tagged query to generate types. Since views aren't written yet, create a stub query file temporarily and run:

```bash
cd dashboard && npm run relay
```

If there are no graphql tags yet, the compiler will exit cleanly with no output. That's fine — we'll run it again after Task 5.

- [ ] **Step 3: Commit**

```bash
git add dashboard/src/App.tsx
git commit -m "feat: add app shell with routing and bottom nav"
```

---

### Task 5: History view

**Files:**
- Create: `dashboard/src/views/HistoryView.tsx`

The History view shows workouts list newest-first with tag filter chips and expandable workout rows showing blocks → rounds → sets.

- [ ] **Step 1: Create dashboard/src/views/HistoryView.tsx**

```tsx
import { graphql, useLazyLoadQuery } from 'react-relay';
import { useState } from 'react';
import type { HistoryViewQuery as HistoryViewQueryType } from './__generated__/HistoryViewQuery.graphql.js';

const query = graphql`
  query HistoryViewQuery($limit: Int, $tag: String) {
    workouts(limit: $limit, tag: $tag) {
      id
      name
      date
      tags
      sleepHours
      notes
      blocks {
        id
        name
        order
        scheme
        rounds {
          round
          sets {
            id
            exerciseName
            weightLbs
            reps
            rpe
            durationSecs
            distanceM
            calories
            watts
            notes
          }
        }
      }
    }
  }
`;

type Workout = HistoryViewQueryType['response']['workouts'][number];
type Block = Workout['blocks'][number];
type Round = Block['rounds'][number];
type Set = Round['sets'][number];

function formatSet(s: Set): string {
  const parts: string[] = [];
  if (s.weightLbs != null && s.reps != null) parts.push(`${s.weightLbs} lbs × ${s.reps}`);
  else if (s.reps != null) parts.push(`${s.reps} reps`);
  else if (s.weightLbs != null) parts.push(`${s.weightLbs} lbs`);
  if (s.rpe != null) parts.push(`@${s.rpe}`);
  if (s.durationSecs != null) parts.push(`${Math.round(s.durationSecs / 60)}min`);
  if (s.distanceM != null) parts.push(`${(s.distanceM / 1000).toFixed(1)}km`);
  if (s.calories != null) parts.push(`${s.calories}cal`);
  if (s.watts != null) parts.push(`${s.watts}W`);
  return parts.join(' · ') || '—';
}

function RoundRow({ round }: { round: Round }) {
  const isSuperSet = round.sets.length > 1;
  return (
    <div style={{ marginBottom: 6 }}>
      {isSuperSet && (
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-3)', marginBottom: 2 }}>
          Round {round.round}
        </div>
      )}
      {round.sets.map((s) => (
        <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, padding: '2px 0', color: 'var(--text-2)' }}>
          <span style={{ fontWeight: 500, color: 'var(--text-1)' }}>{s.exerciseName}</span>
          <span>{formatSet(s)}</span>
        </div>
      ))}
    </div>
  );
}

function BlockSection({ block }: { block: Block }) {
  return (
    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border-light)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)' }}>{block.name}</span>
        {block.scheme && <span style={{ fontSize: 12, color: 'var(--text-3)' }}>{block.scheme}</span>}
      </div>
      {block.rounds.map((r) => (
        <RoundRow key={r.round} round={r} />
      ))}
    </div>
  );
}

function WorkoutRow({ workout }: { workout: Workout }) {
  const [expanded, setExpanded] = useState(false);
  const setCount = workout.blocks.reduce(
    (acc, b) => acc + b.rounds.reduce((a, r) => a + r.sets.length, 0),
    0
  );

  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div
        style={{ padding: '14px 16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <div style={{ fontWeight: 600, fontSize: 15 }}>{workout.name}</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
            {workout.date} · {setCount} sets
            {workout.sleepHours != null && ` · 😴 ${workout.sleepHours}h`}
          </div>
          {workout.tags.length > 0 && (
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
              {workout.tags.map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
          )}
        </div>
        <span style={{ color: 'var(--text-3)', fontSize: 18, marginTop: 2 }}>{expanded ? '▲' : '▼'}</span>
      </div>
      {expanded && (
        <div style={{ padding: '0 16px 14px' }}>
          {workout.notes && (
            <div style={{ fontSize: 12, color: 'var(--text-2)', marginBottom: 8, fontStyle: 'italic' }}>{workout.notes}</div>
          )}
          {workout.blocks.map((b) => <BlockSection key={b.id} block={b} />)}
        </div>
      )}
    </div>
  );
}

const ALL_TAGS = null;

function HistoryContent({ tag }: { tag: string | null }) {
  const data = useLazyLoadQuery<HistoryViewQueryType>(query, { limit: 50, tag: tag ?? undefined });
  const workouts = data.workouts;

  if (workouts.length === 0) {
    return <p style={{ textAlign: 'center', color: 'var(--text-3)', marginTop: 32 }}>No workouts found.</p>;
  }

  return (
    <div>
      {workouts.map((w) => <WorkoutRow key={w.id} workout={w} />)}
    </div>
  );
}

export default function HistoryView() {
  const [activeTag, setActiveTag] = useState<string | null>(null);

  // Common tags as quick filters — shown as chips
  const QUICK_TAGS = ['upper', 'lower', 'squad', 'cardio'];

  return (
    <div style={{ paddingTop: 16 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
        <button
          className={`tag-btn${activeTag === null ? ' active' : ''}`}
          onClick={() => setActiveTag(null)}
        >
          All
        </button>
        {QUICK_TAGS.map((t) => (
          <button
            key={t}
            className={`tag-btn${activeTag === t ? ' active' : ''}`}
            onClick={() => setActiveTag(activeTag === t ? null : t)}
          >
            {t}
          </button>
        ))}
      </div>
      <HistoryContent tag={activeTag} />
    </div>
  );
}
```

- [ ] **Step 2: Run relay compiler to generate types**

```bash
cd dashboard && npm run relay
```

Expected: `dashboard/src/views/__generated__/HistoryViewQuery.graphql.ts` created.

- [ ] **Step 3: Check TypeScript**

```bash
cd dashboard && npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/views/HistoryView.tsx dashboard/src/views/__generated__/
git commit -m "feat: add history view with tag filter and expandable workout rows"
```

Wait — `__generated__/` is in `.gitignore`. Verify the `.gitignore` pattern. If `src/**/__generated__/` is gitignored, do NOT commit generated files. Instead commit only `HistoryView.tsx` and rely on developers to run `npm run relay` themselves.

```bash
git add dashboard/src/views/HistoryView.tsx
git commit -m "feat: add history view with tag filter and expandable workout rows"
```

---

### Task 6: Progress view

**Files:**
- Create: `dashboard/src/views/ProgressView.tsx`

The Progress view lets users select any exercise (with Big 4 preset buttons) and shows a PR table and a weight-over-time SVG sparkline.

- [ ] **Step 1: Create dashboard/src/views/ProgressView.tsx**

```tsx
import { graphql, useLazyLoadQuery } from 'react-relay';
import { useState, Suspense } from 'react';
import type { ProgressViewProgressQuery as ProgressQueryType } from './__generated__/ProgressViewProgressQuery.graphql.js';
import type { ProgressViewExercisesQuery as ExercisesQueryType } from './__generated__/ProgressViewExercisesQuery.graphql.js';

const progressQuery = graphql`
  query ProgressViewProgressQuery($exerciseName: String!) {
    progress(exerciseName: $exerciseName) {
      exerciseName
      prs {
        reps
        weightLbs
        date
      }
      history {
        date
        weightLbs
        reps
      }
    }
  }
`;

const exercisesQuery = graphql`
  query ProgressViewExercisesQuery {
    exercises {
      id
      name
    }
  }
`;

const BIG_4 = ['Back Squat', 'Deadlift', 'Bench Press', 'Pull-ups'];

type Pr = { reps: number; weightLbs: number; date: string };
type HistoryEntry = { date: string; weightLbs: number | null | undefined; reps: number | null | undefined };

function Sparkline({ history }: { history: readonly HistoryEntry[] }) {
  // Show best weight per date
  const byDate = new Map<string, number>();
  for (const h of history) {
    if (h.weightLbs != null) {
      const prev = byDate.get(h.date) ?? 0;
      if (h.weightLbs > prev) byDate.set(h.date, h.weightLbs);
    }
  }
  const points = Array.from(byDate.entries()).sort(([a], [b]) => a.localeCompare(b));
  if (points.length < 2) return null;

  const W = 300;
  const H = 80;
  const pad = 8;
  const weights = points.map(([, w]) => w);
  const minW = Math.min(...weights);
  const maxW = Math.max(...weights);
  const range = maxW - minW || 1;

  const toX = (_: string, i: number) => pad + (i / (points.length - 1)) * (W - pad * 2);
  const toY = (w: number) => H - pad - ((w - minW) / range) * (H - pad * 2);

  const d = points
    .map(([, w], i) => `${i === 0 ? 'M' : 'L'}${toX('', i).toFixed(1)},${toY(w).toFixed(1)}`)
    .join(' ');

  const lastX = toX('', points.length - 1);
  const lastY = toY(weights[weights.length - 1]);

  return (
    <div style={{ marginTop: 16, overflowX: 'auto' }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-3)', marginBottom: 4 }}>Weight over time</div>
      <svg width={W} height={H} style={{ display: 'block' }}>
        <path d={d} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={lastX} cy={lastY} r={4} fill="var(--accent)" />
        <text x={lastX + 6} y={lastY + 4} fontSize={10} fill="var(--accent)" fontWeight="600">
          {weights[weights.length - 1]} lbs
        </text>
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-3)', marginTop: 2, paddingLeft: pad, paddingRight: pad }}>
        <span>{points[0][0]}</span>
        <span>{points[points.length - 1][0]}</span>
      </div>
    </div>
  );
}

function PrTable({ prs }: { prs: readonly Pr[] }) {
  if (prs.length === 0) {
    return <p style={{ fontSize: 13, color: 'var(--text-3)', marginTop: 8 }}>No PR data yet.</p>;
  }
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, marginTop: 8 }}>
      <thead>
        <tr style={{ borderBottom: '1px solid var(--border)' }}>
          <th style={{ textAlign: 'left', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Reps</th>
          <th style={{ textAlign: 'right', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Weight</th>
          <th style={{ textAlign: 'right', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Date</th>
        </tr>
      </thead>
      <tbody>
        {[...prs].sort((a, b) => a.reps - b.reps).map((pr) => (
          <tr key={pr.reps} style={{ borderBottom: '1px solid var(--border-light)' }}>
            <td style={{ padding: '8px 0', fontWeight: 600 }}>{pr.reps}</td>
            <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--green)', fontWeight: 700 }}>{pr.weightLbs} lbs</td>
            <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--text-3)' }}>{pr.date}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ProgressContent({ exerciseName }: { exerciseName: string }) {
  const data = useLazyLoadQuery<ProgressQueryType>(progressQuery, { exerciseName });
  const { prs, history } = data.progress;

  return (
    <div className="card" style={{ padding: '16px' }}>
      <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{exerciseName}</div>
      <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 12 }}>
        {history.length} sets logged
      </div>
      <PrTable prs={prs} />
      <Sparkline history={history} />
    </div>
  );
}

function ExercisePicker({ value, onChange }: { value: string; onChange: (name: string) => void }) {
  const data = useLazyLoadQuery<ExercisesQueryType>(exercisesQuery, {});
  const exercises = data.exercises.map((e) => e.name).sort();
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: '100%', padding: '10px 12px', fontSize: 14,
        borderRadius: 'var(--radius-sm)', border: '1.5px solid var(--border)',
        background: 'var(--card)', color: 'var(--text-1)', cursor: 'pointer',
      }}
    >
      {exercises.map((name) => (
        <option key={name} value={name}>{name}</option>
      ))}
    </select>
  );
}

export default function ProgressView() {
  const [selected, setSelected] = useState(BIG_4[0]);

  return (
    <div style={{ paddingTop: 16 }}>
      {/* Big 4 preset buttons */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
        {BIG_4.map((name) => (
          <button
            key={name}
            className={`tag-btn${selected === name ? ' active' : ''}`}
            onClick={() => setSelected(name)}
          >
            {name}
          </button>
        ))}
      </div>

      {/* All exercises picker */}
      <div style={{ marginBottom: 16 }}>
        <Suspense fallback={null}>
          <ExercisePicker value={selected} onChange={setSelected} />
        </Suspense>
      </div>

      {/* Progress card */}
      <Suspense fallback={<p style={{ textAlign: 'center', color: 'var(--text-3)', marginTop: 32 }}>Loading…</p>}>
        <ProgressContent exerciseName={selected} />
      </Suspense>
    </div>
  );
}
```

- [ ] **Step 2: Run relay compiler**

```bash
cd dashboard && npm run relay
```

Expected: Two files generated:
- `dashboard/src/views/__generated__/ProgressViewProgressQuery.graphql.ts`
- `dashboard/src/views/__generated__/ProgressViewExercisesQuery.graphql.ts`

- [ ] **Step 3: Check TypeScript**

```bash
cd dashboard && npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/views/ProgressView.tsx
git commit -m "feat: add progress view with PR table and weight-over-time sparkline"
```

---

### Task 7: Smoke test — verify dev server starts

**Files:** (no new files)

- [ ] **Step 1: Ensure gym GraphQL server is running**

The GraphQL server must be running on port 47322 for the Vite proxy to work. Check:

```bash
curl -s -X POST http://localhost:47322/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ exercises { id name } }"}' | head -c 100
```

Expected: JSON response (may be `{"data":{"exercises":[]}}` if DB is empty).

If the server is not running, start it:
```bash
cd server && npm run dev &
```

- [ ] **Step 2: Start the dashboard dev server**

```bash
cd dashboard && npm run dev
```

Expected: `VITE v5.x.x  ready in xxx ms` and `➜  Local: http://localhost:47323/`

- [ ] **Step 3: Verify relay-compiled types exist**

```bash
ls dashboard/src/views/__generated__/
```

Expected: At least `HistoryViewQuery.graphql.ts` and `ProgressViewProgressQuery.graphql.ts` and `ProgressViewExercisesQuery.graphql.ts`.

If missing, run:
```bash
cd dashboard && npm run relay
```

- [ ] **Step 4: Commit remaining files**

```bash
git status
git add -A -- dashboard/
git commit -m "chore: add dashboard gitignore and any remaining config"
```

Only commit files that are NOT gitignored (i.e., not `node_modules/`, `dist/`, `__generated__/`).

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| History view: workouts list newest-first | Task 5 |
| Filterable by tag | Task 5 — tag chips |
| Expandable rows: blocks → rounds → sets | Task 5 — WorkoutRow / BlockSection / RoundRow |
| Progress: Big 4 spotlight | Task 6 — BIG_4 preset buttons |
| Progress: PR table | Task 6 — PrTable |
| Progress: weight-over-time chart | Task 6 — Sparkline SVG |
| Progress: any exercise | Task 6 — ExercisePicker from exercises query |
| Mobile-first (iPhone 14 Pro) | Tasks 3+5+6 — max-width 720px, bottom nav |
| Port 47323 | Task 1 — vite.config.ts |
| Proxy to 47322 | Task 1 — vite.config.ts |

All spec requirements covered. No placeholders.
