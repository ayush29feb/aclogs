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
