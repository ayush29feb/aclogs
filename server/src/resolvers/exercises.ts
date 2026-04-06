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
