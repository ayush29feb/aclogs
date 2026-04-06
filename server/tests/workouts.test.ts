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
