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
    id: String(row.id),
    name: row.name,
    date: row.date,
    sleepHours: row.sleep_hours != null ? Number(row.sleep_hours) : null,
    tags,
    notes: row.notes ?? null,
  };
}

function setToGql(row: DBSet) {
  return {
    id: String(row.id),
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
  if (workoutIds.length === 0) return new Map<number, any[]>();
  const idList = workoutIds.join(',');
  const blocks = await prisma.$queryRawUnsafe<DBBlock[]>(
    `SELECT id, workout_id, name, "order", scheme FROM blocks WHERE workout_id IN (${idList}) ORDER BY workout_id, "order"`
  );

  const blockIds = blocks.map((b) => Number(b.id));
  if (blockIds.length === 0) return new Map(workoutIds.map((id) => [id, []]));

  const sets = await prisma.$queryRawUnsafe<DBSet[]>(`
    SELECT s.id, s.block_id, s.exercise_id, e.name as exercise_name, s.round,
           s.weight_lbs, s.reps, s.rpe, s.duration_secs, s.distance_m,
           s.calories, s.watts, s.notes, CAST(s.logged_at AS TEXT) as logged_at
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

  const blocksByWorkout = new Map<number, any[]>();
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
      id: String(b.id),
      name: b.name,
      order: Number(b.order),
      scheme: b.scheme ?? null,
      rounds,
    });
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
        let filtered = rows;
        if (args.tag) {
          filtered = rows.filter((r) => {
            try { return (JSON.parse(r.tags ?? '[]') as string[]).includes(args.tag!); } catch { return false; }
          });
        }
        const ids = filtered.map((r) => Number(r.id));
        const blocksByWorkout = await fetchBlocksWithSets(prisma, ids);
        return filtered.map((r) => {
          const w = workoutToGql(r);
          return { ...w, blocks: blocksByWorkout.get(Number(r.id)) ?? [] };
        });
      },

      async workout(_: unknown, args: { id: number }) {
        const rows = await prisma.$queryRawUnsafe<DBWorkout[]>(
          `SELECT id, name, date, sleep_hours, tags, notes, photo_path FROM workouts WHERE id = ${args.id}`
        );
        if (rows.length === 0) return null;
        const numId = Number(rows[0].id);
        const w = workoutToGql(rows[0]);
        const blocksByWorkout = await fetchBlocksWithSets(prisma, [numId]);
        return { ...w, blocks: blocksByWorkout.get(numId) ?? [] };
      },
    },
  };
}
