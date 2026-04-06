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
