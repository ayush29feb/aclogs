import { PrismaClient } from '@prisma/client';

export function buildResolvers(_prisma: PrismaClient) {
  return {
    Query: {
      exercises: () => [],
    },
  };
}
