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
