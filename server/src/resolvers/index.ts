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
