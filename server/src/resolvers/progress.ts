import { PrismaClient } from '@prisma/client';

const COMPOUNDS = new Set(['Back Squat', 'Deadlift', 'Bench Press', 'Pull-ups', 'Strict Press', 'Chin-up']);

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
          `SELECT id, name FROM exercises WHERE name = ?`,
          args.exerciseName
        );

        if (exRows.length === 0) {
          return { exerciseName: args.exerciseName, prs: [], history: [] };
        }

        const primaryId = Number(exRows[0].id);
        let exerciseIds: number[] = [primaryId];

        if (args.related) {
          const relRows = await prisma.$queryRawUnsafe<{ other_id: number }[]>(`
            SELECT related_exercise_id as other_id FROM exercise_relations WHERE exercise_id = ?
            UNION
            SELECT exercise_id as other_id FROM exercise_relations WHERE related_exercise_id = ?
          `, primaryId, primaryId);
          const relIds = relRows.map((r) => Number(r.other_id));
          exerciseIds = [...new Set([primaryId, ...relIds])];
        }

        const placeholders = exerciseIds.map(() => '?').join(',');
        const rows = await prisma.$queryRawUnsafe<DBSetRow[]>(`
          SELECT CAST(w.date AS TEXT) as date, e.name as exercise_name,
                 s.weight_lbs, s.reps, s.rpe, s.watts, s.calories, s.duration_secs
          FROM sets s
          JOIN blocks b ON b.id = s.block_id
          JOIN workouts w ON w.id = b.workout_id
          JOIN exercises e ON e.id = s.exercise_id
          WHERE s.exercise_id IN (${placeholders})
          ORDER BY w.date ASC
        `, ...exerciseIds);

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

      async exercisePrs() {
        const rows = await prisma.$queryRawUnsafe<{ name: string; reps: number; max_weight: number }[]>(`
          SELECT e.name, s.reps, MAX(s.weight_lbs) as max_weight
          FROM sets s
          JOIN exercises e ON e.id = s.exercise_id
          WHERE s.reps IN (1, 3, 5, 8) AND s.weight_lbs IS NOT NULL
          GROUP BY e.id, s.reps
          ORDER BY e.name, s.reps
        `);

        const byExercise = new Map<string, { pr1?: number; pr3?: number; pr5?: number; pr8?: number }>();
        for (const row of rows) {
          if (!byExercise.has(row.name)) byExercise.set(row.name, {});
          const entry = byExercise.get(row.name)!;
          const reps = Number(row.reps);
          const w = Number(row.max_weight);
          if (reps === 1) entry.pr1 = w;
          else if (reps === 3) entry.pr3 = w;
          else if (reps === 5) entry.pr5 = w;
          else if (reps === 8) entry.pr8 = w;
        }

        return Array.from(byExercise.entries())
          .map(([name, prs]) => ({ exerciseName: name, isCompound: COMPOUNDS.has(name), ...prs }))
          .sort((a, b) => {
            if (a.isCompound && !b.isCompound) return -1;
            if (!a.isCompound && b.isCompound) return 1;
            return a.exerciseName.localeCompare(b.exerciseName);
          });
      },
    },
  };
}
