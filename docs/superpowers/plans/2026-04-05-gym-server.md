# Gym GraphQL Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only GraphQL server that reads from the SQLite DB written by the Python CLI and exposes workout history, exercise data, and progress PRs to the dashboard.

**Architecture:** Node.js + graphql-yoga + Prisma 5 pointing at the same `gym.db` SQLite file the CLI writes. The server is read-only — all writes happen via the CLI. Resolvers use `$queryRawUnsafe` for complex joins. Port 47322.

**Tech Stack:** Node.js 20, TypeScript 5, graphql-yoga 5, Prisma 5, vitest 2, tsx 4

---

## File Structure

| File | Purpose |
|------|---------|
| `server/package.json` | npm workspace config, scripts, deps |
| `server/tsconfig.json` | TypeScript config |
| `server/.env.example` | `DATABASE_URL=file:../data/gym.db` template |
| `server/prisma/schema.prisma` | Prisma schema mapping all 5 SQLAlchemy models |
| `server/src/schema.ts` | GraphQL SDL (`typeDefs` export) |
| `server/src/db.ts` | Prisma client singleton |
| `server/src/yoga.ts` | `createApp(prisma)` factory (testable) |
| `server/src/resolvers/index.ts` | `buildResolvers(prisma)` combining all resolvers |
| `server/src/resolvers/exercises.ts` | `exercises` + `exercise` queries |
| `server/src/resolvers/workouts.ts` | `workouts` + `workout` queries with nested blocks/sets |
| `server/src/resolvers/progress.ts` | `progress` query with optional related-exercise traversal |
| `server/src/test-utils.ts` | `createTestYoga(prisma)` + `gql(yoga, query)` helpers |
| `server/src/index.ts` | HTTP server on port 47322 |
| `server/tests/exercises.test.ts` | Exercise resolver tests |
| `server/tests/workouts.test.ts` | Workout resolver tests |
| `server/tests/progress.test.ts` | Progress resolver tests |

---

### Task 1: Project scaffolding

**Files:**
- Create: `server/package.json`
- Create: `server/tsconfig.json`
- Create: `server/.env.example`

- [ ] **Step 1: Create server/package.json**

```json
{
  "name": "gym-server",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch --env-file=.env src/index.ts",
    "build": "tsc",
    "start": "node --env-file=.env dist/index.js",
    "test": "vitest run",
    "db:generate": "prisma generate"
  },
  "dependencies": {
    "@prisma/client": "^5.22.0",
    "graphql": "^16.9.0",
    "graphql-yoga": "^5.10.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "prisma": "^5.22.0",
    "tsx": "^4.19.0",
    "typescript": "^5.5.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create server/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3: Create server/.env.example**

```
DATABASE_URL=file:../data/gym.db
PORT=47322
```

- [ ] **Step 4: Install dependencies**

```bash
cd server && npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 5: Commit**

```bash
git add server/package.json server/tsconfig.json server/.env.example
git commit -m "chore: scaffold gym GraphQL server project"
```

---

### Task 2: Prisma schema

**Files:**
- Create: `server/prisma/schema.prisma`

- [ ] **Step 1: Write the failing test (manual verification)**

We'll verify in Task 4 once db:generate works. For now, just create the schema.

- [ ] **Step 2: Create server/prisma/schema.prisma**

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

model Exercise {
  id           Int               @id @default(autoincrement())
  name         String            @unique
  muscle_group String?
  notes        String?
  sets         Set[]
  relations    ExerciseRelation[] @relation("ExerciseRelations")
  related_by   ExerciseRelation[] @relation("RelatedExerciseRelations")

  @@map("exercises")
}

model Workout {
  id          Int     @id @default(autoincrement())
  name        String
  date        String
  sleep_hours Float?
  tags        String?
  notes       String?
  photo_path  String?
  blocks      Block[]

  @@map("workouts")
}

model Block {
  id         Int     @id @default(autoincrement())
  workout_id Int
  name       String
  order      Int
  scheme     String?
  workout    Workout @relation(fields: [workout_id], references: [id])
  sets       Set[]

  @@map("blocks")
}

model Set {
  id            Int      @id @default(autoincrement())
  block_id      Int
  exercise_id   Int
  round         Int
  weight_lbs    Float?
  reps          Int?
  rpe           Float?
  duration_secs Int?
  distance_m    Float?
  calories      Float?
  watts         Float?
  notes         String?
  logged_at     String
  block         Block    @relation(fields: [block_id], references: [id])
  exercise      Exercise @relation(fields: [exercise_id], references: [id])

  @@map("sets")
}

model ExerciseRelation {
  exercise_id         Int
  related_exercise_id Int
  relation_type       String   @default("variant")
  exercise            Exercise @relation("ExerciseRelations", fields: [exercise_id], references: [id])
  related_exercise    Exercise @relation("RelatedExerciseRelations", fields: [related_exercise_id], references: [id])

  @@id([exercise_id, related_exercise_id])
  @@map("exercise_relations")
}
```

- [ ] **Step 3: Generate Prisma client**

```bash
cd server && DATABASE_URL=file:../data/gym.db npx prisma generate
```

Expected: `Generated Prisma Client` — no errors.

- [ ] **Step 4: Commit**

```bash
git add server/prisma/schema.prisma server/node_modules/.prisma
git commit -m "feat: add Prisma schema for gym SQLite models"
```

Note: only commit `schema.prisma`; the generated client in `node_modules` is not committed.

```bash
git add server/prisma/schema.prisma
git commit -m "feat: add Prisma schema for gym SQLite models"
```

---

### Task 3: GraphQL SDL schema

**Files:**
- Create: `server/src/schema.ts`

- [ ] **Step 1: Create server/src/schema.ts**

```typescript
export const typeDefs = /* GraphQL */ `
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

  type PrEntry {
    weightLbs: Float!
    date: String!
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
`;
```

- [ ] **Step 2: Commit**

```bash
git add server/src/schema.ts
git commit -m "feat: add GraphQL SDL schema for gym server"
```

---

### Task 4: Yoga factory + test utilities

**Files:**
- Create: `server/src/yoga.ts`
- Create: `server/src/test-utils.ts`

- [ ] **Step 1: Write failing test**

Create `server/tests/smoke.test.ts`:

```typescript
import { describe, it, expect, afterEach } from 'vitest';
import { PrismaClient } from '@prisma/client';
import { createTestYoga, gql } from '../src/test-utils.js';

describe('smoke', () => {
  let prisma: PrismaClient;

  afterEach(async () => {
    await prisma.$disconnect();
  });

  it('returns empty exercises list', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{ exercises { id name } }`);
    expect(result.errors).toBeUndefined();
    expect(Array.isArray(result.data.exercises)).toBe(true);
  });
});
```

- [ ] **Step 2: Run to confirm it fails (missing modules)**

```bash
cd server && npm test -- tests/smoke.test.ts
```

Expected: FAIL — `Cannot find module '../src/test-utils.js'`

- [ ] **Step 3: Create server/src/yoga.ts**

```typescript
import { createYoga, createSchema } from 'graphql-yoga';
import { PrismaClient } from '@prisma/client';
import { typeDefs } from './schema.js';
import { buildResolvers } from './resolvers/index.js';

export function createApp(prisma: PrismaClient) {
  return createYoga({
    schema: createSchema({
      typeDefs,
      resolvers: buildResolvers(prisma) as any,
    }),
  });
}
```

- [ ] **Step 4: Create server/src/test-utils.ts**

```typescript
import { createYoga, createSchema } from 'graphql-yoga';
import { PrismaClient } from '@prisma/client';
import { typeDefs } from './schema.js';
import { buildResolvers } from './resolvers/index.js';

export function createTestYoga(prisma: PrismaClient) {
  return createYoga({
    schema: createSchema({
      typeDefs,
      resolvers: buildResolvers(prisma) as any,
    }),
    logging: false,
  });
}

export async function gql(
  yoga: ReturnType<typeof createYoga>,
  query: string,
  variables?: Record<string, unknown>
) {
  const res = await yoga.fetch('http://localhost/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  return res.json() as Promise<{ data: Record<string, unknown>; errors?: unknown[] }>;
}
```

- [ ] **Step 5: Create stub server/src/resolvers/index.ts** (needed for imports to resolve)

```typescript
import { PrismaClient } from '@prisma/client';

export function buildResolvers(_prisma: PrismaClient) {
  return {
    Query: {},
  };
}
```

- [ ] **Step 6: Run test to verify it passes**

```bash
cd server && npm test -- tests/smoke.test.ts
```

Expected: PASS (empty resolvers returns empty array)

- [ ] **Step 7: Commit**

```bash
git add server/src/yoga.ts server/src/test-utils.ts server/src/resolvers/index.ts server/tests/smoke.test.ts
git commit -m "feat: add yoga factory and test utilities"
```

---

### Task 5: Exercise resolver

**Files:**
- Create: `server/src/resolvers/exercises.ts`
- Modify: `server/src/resolvers/index.ts`
- Create: `server/tests/exercises.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `server/tests/exercises.test.ts`:

```typescript
import { describe, it, expect, afterEach } from 'vitest';
import { PrismaClient } from '@prisma/client';
import { createTestYoga, gql } from '../src/test-utils.js';

describe('exercises', () => {
  let prisma: PrismaClient;

  afterEach(async () => {
    await prisma.$disconnect();
  });

  it('exercises returns array', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{
      exercises { id name muscleGroup notes relatedExercises { id name } }
    }`);
    expect(result.errors).toBeUndefined();
    expect(Array.isArray(result.data.exercises)).toBe(true);
  });

  it('exercise by name returns null for missing', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{ exercise(name: "__nonexistent__") { id name } }`);
    expect(result.errors).toBeUndefined();
    expect(result.data.exercise).toBeNull();
  });
});
```

- [ ] **Step 2: Run to verify fails**

```bash
cd server && npm test -- tests/exercises.test.ts
```

Expected: FAIL — `exercises is not a field on Query` (stub resolvers have no exercises field)

- [ ] **Step 3: Create server/src/resolvers/exercises.ts**

```typescript
import { PrismaClient } from '@prisma/client';

type DBExercise = {
  id: number;
  name: string;
  muscle_group: string | null;
  notes: string | null;
};

type DBRelation = {
  exercise_id: number;
  related_exercise_id: number;
  rel_id: number;
  rel_name: string;
  rel_muscle_group: string | null;
  rel_notes: string | null;
};

export function exerciseResolvers(prisma: PrismaClient) {
  return {
    Query: {
      async exercises() {
        const rows = await prisma.$queryRawUnsafe<DBExercise[]>(
          `SELECT id, name, muscle_group, notes FROM exercises ORDER BY name`
        );
        return rows.map(toGql);
      },

      async exercise(_: unknown, args: { name: string }) {
        const rows = await prisma.$queryRawUnsafe<DBExercise[]>(
          `SELECT id, name, muscle_group, notes FROM exercises WHERE name = '${args.name.replace(/'/g, "''")}'`
        );
        return rows.length > 0 ? toGql(rows[0]) : null;
      },
    },

    Exercise: {
      async relatedExercises(exercise: { id: number }) {
        const rows = await prisma.$queryRawUnsafe<DBRelation[]>(`
          SELECT er.exercise_id, er.related_exercise_id,
                 e.id as rel_id, e.name as rel_name, e.muscle_group as rel_muscle_group, e.notes as rel_notes
          FROM exercise_relations er
          JOIN exercises e ON e.id = er.related_exercise_id
          WHERE er.exercise_id = ${exercise.id}
          UNION
          SELECT er.exercise_id, er.related_exercise_id,
                 e.id as rel_id, e.name as rel_name, e.muscle_group as rel_muscle_group, e.notes as rel_notes
          FROM exercise_relations er
          JOIN exercises e ON e.id = er.exercise_id
          WHERE er.related_exercise_id = ${exercise.id}
        `);
        return rows.map((r) => ({
          id: Number(r.rel_id),
          name: r.rel_name,
          muscleGroup: r.rel_muscle_group ?? null,
          notes: r.rel_notes ?? null,
        }));
      },
    },
  };
}

function toGql(row: DBExercise) {
  return {
    id: Number(row.id),
    name: row.name,
    muscleGroup: row.muscle_group ?? null,
    notes: row.notes ?? null,
  };
}
```

- [ ] **Step 4: Update server/src/resolvers/index.ts**

```typescript
import { PrismaClient } from '@prisma/client';
import { exerciseResolvers } from './exercises.js';

export function buildResolvers(prisma: PrismaClient) {
  const exercises = exerciseResolvers(prisma);

  return {
    Query: {
      ...exercises.Query,
    },
    Exercise: exercises.Exercise,
  };
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd server && npm test -- tests/exercises.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add server/src/resolvers/exercises.ts server/src/resolvers/index.ts server/tests/exercises.test.ts
git commit -m "feat: add exercise resolver with related exercises"
```

---

### Task 6: Workout resolver

**Files:**
- Create: `server/src/resolvers/workouts.ts`
- Modify: `server/src/resolvers/index.ts`
- Create: `server/tests/workouts.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `server/tests/workouts.test.ts`:

```typescript
import { describe, it, expect, afterEach } from 'vitest';
import { PrismaClient } from '@prisma/client';
import { createTestYoga, gql } from '../src/test-utils.js';

describe('workouts', () => {
  let prisma: PrismaClient;

  afterEach(async () => {
    await prisma.$disconnect();
  });

  it('workouts returns array', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{
      workouts(limit: 5) {
        id name date sleepHours tags notes
        blocks { id name order scheme
          rounds { round sets { id exerciseName round weightLbs reps rpe loggedAt } }
        }
      }
    }`);
    expect(result.errors).toBeUndefined();
    expect(Array.isArray(result.data.workouts)).toBe(true);
  });

  it('workout by id returns null for missing', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{ workout(id: 999999) { id name } }`);
    expect(result.errors).toBeUndefined();
    expect(result.data.workout).toBeNull();
  });

  it('workouts filtered by tag returns matching workouts', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{ workouts(tag: "__no_such_tag__") { id tags } }`);
    expect(result.errors).toBeUndefined();
    expect(result.data.workouts).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify fails**

```bash
cd server && npm test -- tests/workouts.test.ts
```

Expected: FAIL — `workouts is not a field on Query`

- [ ] **Step 3: Create server/src/resolvers/workouts.ts**

```typescript
import { PrismaClient } from '@prisma/client';

type DBWorkout = {
  id: number;
  name: string;
  date: string;
  sleep_hours: number | null;
  tags: string | null;
  notes: string | null;
  photo_path: string | null;
};

type DBBlock = {
  id: number;
  workout_id: number;
  name: string;
  order: number;
  scheme: string | null;
};

type DBSet = {
  id: number;
  block_id: number;
  exercise_id: number;
  exercise_name: string;
  round: number;
  weight_lbs: number | null;
  reps: number | null;
  rpe: number | null;
  duration_secs: number | null;
  distance_m: number | null;
  calories: number | null;
  watts: number | null;
  notes: string | null;
  logged_at: string;
};

function workoutToGql(row: DBWorkout) {
  let tags: string[] = [];
  if (row.tags) {
    try {
      tags = JSON.parse(row.tags);
    } catch {
      tags = [];
    }
  }
  return {
    id: Number(row.id),
    name: row.name,
    date: row.date,
    sleepHours: row.sleep_hours != null ? Number(row.sleep_hours) : null,
    tags,
    notes: row.notes ?? null,
  };
}

function setToGql(row: DBSet) {
  return {
    id: Number(row.id),
    exerciseId: Number(row.exercise_id),
    exerciseName: row.exercise_name,
    round: Number(row.round),
    weightLbs: row.weight_lbs != null ? Number(row.weight_lbs) : null,
    reps: row.reps != null ? Number(row.reps) : null,
    rpe: row.rpe != null ? Number(row.rpe) : null,
    durationSecs: row.duration_secs != null ? Number(row.duration_secs) : null,
    distanceM: row.distance_m != null ? Number(row.distance_m) : null,
    calories: row.calories != null ? Number(row.calories) : null,
    watts: row.watts != null ? Number(row.watts) : null,
    notes: row.notes ?? null,
    loggedAt: row.logged_at,
  };
}

async function fetchBlocksWithSets(prisma: PrismaClient, workoutIds: number[]) {
  if (workoutIds.length === 0) return new Map<number, DBBlock[]>();
  const idList = workoutIds.join(',');
  const blocks = await prisma.$queryRawUnsafe<DBBlock[]>(
    `SELECT id, workout_id, name, "order", scheme FROM blocks WHERE workout_id IN (${idList}) ORDER BY workout_id, "order"`
  );

  const blockIds = blocks.map((b) => Number(b.id));
  if (blockIds.length === 0) return new Map(workoutIds.map((id) => [id, []]));

  const sets = await prisma.$queryRawUnsafe<DBSet[]>(`
    SELECT s.id, s.block_id, s.exercise_id, e.name as exercise_name, s.round,
           s.weight_lbs, s.reps, s.rpe, s.duration_secs, s.distance_m,
           s.calories, s.watts, s.notes, s.logged_at
    FROM sets s
    JOIN exercises e ON e.id = s.exercise_id
    WHERE s.block_id IN (${blockIds.join(',')})
    ORDER BY s.block_id, s.round
  `);

  const setsByBlock = new Map<number, DBSet[]>();
  for (const s of sets) {
    const bid = Number(s.block_id);
    if (!setsByBlock.has(bid)) setsByBlock.set(bid, []);
    setsByBlock.get(bid)!.push(s);
  }

  const blocksByWorkout = new Map<number, DBBlock[]>();
  for (const b of blocks) {
    const wid = Number(b.workout_id);
    if (!blocksByWorkout.has(wid)) blocksByWorkout.set(wid, []);
    const blockSets = setsByBlock.get(Number(b.id)) ?? [];

    // Group sets by round number
    const roundMap = new Map<number, DBSet[]>();
    for (const s of blockSets) {
      const r = Number(s.round);
      if (!roundMap.has(r)) roundMap.set(r, []);
      roundMap.get(r)!.push(s);
    }
    const rounds = Array.from(roundMap.entries())
      .sort(([a], [b]) => a - b)
      .map(([round, roundSets]) => ({
        round,
        sets: roundSets.map(setToGql),
      }));

    blocksByWorkout.get(wid)!.push({
      id: Number(b.id),
      name: b.name,
      order: Number(b.order),
      scheme: b.scheme ?? null,
      rounds,
    } as any);
  }

  return blocksByWorkout;
}

export function workoutResolvers(prisma: PrismaClient) {
  return {
    Query: {
      async workouts(_: unknown, args: { limit?: number; tag?: string }) {
        const limit = args.limit ?? 20;
        const rows = await prisma.$queryRawUnsafe<DBWorkout[]>(
          `SELECT id, name, date, sleep_hours, tags, notes, photo_path FROM workouts ORDER BY date DESC LIMIT ${limit}`
        );
        let workouts = rows.map(workoutToGql);
        if (args.tag) {
          workouts = workouts.filter((w) => w.tags.includes(args.tag!));
        }
        const ids = workouts.map((w) => w.id);
        const blocksByWorkout = await fetchBlocksWithSets(prisma, ids);
        return workouts.map((w) => ({ ...w, blocks: blocksByWorkout.get(w.id) ?? [] }));
      },

      async workout(_: unknown, args: { id: number }) {
        const rows = await prisma.$queryRawUnsafe<DBWorkout[]>(
          `SELECT id, name, date, sleep_hours, tags, notes, photo_path FROM workouts WHERE id = ${args.id}`
        );
        if (rows.length === 0) return null;
        const w = workoutToGql(rows[0]);
        const blocksByWorkout = await fetchBlocksWithSets(prisma, [w.id]);
        return { ...w, blocks: blocksByWorkout.get(w.id) ?? [] };
      },
    },
  };
}
```

- [ ] **Step 4: Update server/src/resolvers/index.ts**

```typescript
import { PrismaClient } from '@prisma/client';
import { exerciseResolvers } from './exercises.js';
import { workoutResolvers } from './workouts.js';

export function buildResolvers(prisma: PrismaClient) {
  const exercises = exerciseResolvers(prisma);
  const workouts = workoutResolvers(prisma);

  return {
    Query: {
      ...exercises.Query,
      ...workouts.Query,
    },
    Exercise: exercises.Exercise,
  };
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd server && npm test -- tests/workouts.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add server/src/resolvers/workouts.ts server/src/resolvers/index.ts server/tests/workouts.test.ts
git commit -m "feat: add workout resolver with blocks and rounds"
```

---

### Task 7: Progress resolver

**Files:**
- Create: `server/src/resolvers/progress.ts`
- Modify: `server/src/resolvers/index.ts`
- Create: `server/tests/progress.test.ts`

- [ ] **Step 1: Write the failing tests**

Create `server/tests/progress.test.ts`:

```typescript
import { describe, it, expect, afterEach } from 'vitest';
import { PrismaClient } from '@prisma/client';
import { createTestYoga, gql } from '../src/test-utils.js';

describe('progress', () => {
  let prisma: PrismaClient;

  afterEach(async () => {
    await prisma.$disconnect();
  });

  it('progress for unknown exercise returns empty prs and history', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{
      progress(exerciseName: "__no_such_exercise__") {
        exerciseName
        prs { reps weightLbs date }
        history { date exerciseName weightLbs reps }
      }
    }`);
    expect(result.errors).toBeUndefined();
    const progress = result.data.progress as { exerciseName: string; prs: unknown[]; history: unknown[] };
    expect(progress.exerciseName).toBe('__no_such_exercise__');
    expect(progress.prs).toEqual([]);
    expect(progress.history).toEqual([]);
  });

  it('progress with related flag returns empty for unknown exercise', async () => {
    prisma = new PrismaClient();
    const yoga = createTestYoga(prisma);
    const result = await gql(yoga, `{
      progress(exerciseName: "__no_such_exercise__", related: true) {
        exerciseName prs { reps weightLbs date }
      }
    }`);
    expect(result.errors).toBeUndefined();
    const progress = result.data.progress as { prs: unknown[] };
    expect(progress.prs).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify fails**

```bash
cd server && npm test -- tests/progress.test.ts
```

Expected: FAIL — `progress is not a field on Query`

- [ ] **Step 3: Create server/src/resolvers/progress.ts**

```typescript
import { PrismaClient } from '@prisma/client';

type DBExerciseRow = { id: number; name: string };

type DBSetRow = {
  date: string;
  exercise_name: string;
  weight_lbs: number | null;
  reps: number | null;
  rpe: number | null;
  watts: number | null;
  calories: number | null;
  duration_secs: number | null;
};

export function progressResolvers(prisma: PrismaClient) {
  return {
    Query: {
      async progress(_: unknown, args: { exerciseName: string; related?: boolean }) {
        // Look up the primary exercise
        const exRows = await prisma.$queryRawUnsafe<DBExerciseRow[]>(
          `SELECT id, name FROM exercises WHERE name = '${args.exerciseName.replace(/'/g, "''")}'`
        );

        if (exRows.length === 0) {
          return { exerciseName: args.exerciseName, prs: [], history: [] };
        }

        const primaryId = Number(exRows[0].id);
        let exerciseIds: number[] = [primaryId];

        if (args.related) {
          const relRows = await prisma.$queryRawUnsafe<{ other_id: number }[]>(`
            SELECT related_exercise_id as other_id FROM exercise_relations WHERE exercise_id = ${primaryId}
            UNION
            SELECT exercise_id as other_id FROM exercise_relations WHERE related_exercise_id = ${primaryId}
          `);
          const relIds = relRows.map((r) => Number(r.other_id));
          exerciseIds = [...new Set([primaryId, ...relIds])];
        }

        const idList = exerciseIds.join(',');
        const rows = await prisma.$queryRawUnsafe<DBSetRow[]>(`
          SELECT w.date, e.name as exercise_name,
                 s.weight_lbs, s.reps, s.rpe, s.watts, s.calories, s.duration_secs
          FROM sets s
          JOIN blocks b ON b.id = s.block_id
          JOIN workouts w ON w.id = b.workout_id
          JOIN exercises e ON e.id = s.exercise_id
          WHERE s.exercise_id IN (${idList})
          ORDER BY w.date ASC
        `);

        const history = rows.map((r) => ({
          date: r.date,
          exerciseName: r.exercise_name,
          weightLbs: r.weight_lbs != null ? Number(r.weight_lbs) : null,
          reps: r.reps != null ? Number(r.reps) : null,
          rpe: r.rpe != null ? Number(r.rpe) : null,
          watts: r.watts != null ? Number(r.watts) : null,
          calories: r.calories != null ? Number(r.calories) : null,
          durationSecs: r.duration_secs != null ? Number(r.duration_secs) : null,
        }));

        // Build PRs: max weight per rep count
        const prMap = new Map<number, { weightLbs: number; date: string }>();
        for (const r of rows) {
          if (r.reps != null && r.weight_lbs != null) {
            const reps = Number(r.reps);
            const w = Number(r.weight_lbs);
            const existing = prMap.get(reps);
            if (!existing || w > existing.weightLbs) {
              prMap.set(reps, { weightLbs: w, date: r.date });
            }
          }
        }
        const prs = Array.from(prMap.entries())
          .sort(([a], [b]) => a - b)
          .map(([reps, pr]) => ({ reps, weightLbs: pr.weightLbs, date: pr.date }));

        return { exerciseName: args.exerciseName, prs, history };
      },
    },
  };
}
```

- [ ] **Step 4: Update server/src/resolvers/index.ts**

```typescript
import { PrismaClient } from '@prisma/client';
import { exerciseResolvers } from './exercises.js';
import { workoutResolvers } from './workouts.js';
import { progressResolvers } from './progress.js';

export function buildResolvers(prisma: PrismaClient) {
  const exercises = exerciseResolvers(prisma);
  const workouts = workoutResolvers(prisma);
  const progress = progressResolvers(prisma);

  return {
    Query: {
      ...exercises.Query,
      ...workouts.Query,
      ...progress.Query,
    },
    Exercise: exercises.Exercise,
  };
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd server && npm test -- tests/progress.test.ts
```

Expected: PASS

- [ ] **Step 6: Run all tests**

```bash
cd server && npm test
```

Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add server/src/resolvers/progress.ts server/src/resolvers/index.ts server/tests/progress.test.ts
git commit -m "feat: add progress resolver with PR calculation and related exercise support"
```

---

### Task 8: Server entry point

**Files:**
- Create: `server/src/index.ts`

- [ ] **Step 1: Create server/src/index.ts**

```typescript
import { createServer } from 'node:http';
import { PrismaClient } from '@prisma/client';
import { createApp } from './yoga.js';

const prisma = new PrismaClient();
const port = parseInt(process.env.PORT ?? '47322', 10);

const yoga = createApp(prisma);

const server = createServer(yoga);

server.listen(port, () => {
  console.log(`Gym GraphQL server running at http://localhost:${port}/graphql`);
});

process.on('SIGTERM', async () => {
  await prisma.$disconnect();
  server.close();
});
```

- [ ] **Step 2: Verify the server starts (manual check)**

Create a `.env` file from the example (local only, not committed):
```bash
cp server/.env.example server/.env
```

Then start the server:
```bash
cd server && npm run dev
```

Expected: `Gym GraphQL server running at http://localhost:47322/graphql`

Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add server/src/index.ts
git commit -m "feat: add HTTP server entry point on port 47322"
```

---

### Task 9: Gitignore and cleanup

**Files:**
- Modify: `.gitignore`
- Modify: `server/.gitignore` (new)

- [ ] **Step 1: Create server/.gitignore**

```
node_modules/
dist/
.env
```

- [ ] **Step 2: Run all tests one final time**

```bash
cd server && npm test
```

Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add server/.gitignore
git commit -m "chore: add server gitignore"
```
