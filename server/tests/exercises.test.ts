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
