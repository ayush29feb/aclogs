import { createYoga, createSchema } from 'graphql-yoga';
import { PrismaClient } from '@prisma/client';
import { typeDefs } from './schema.js';
import { buildResolvers } from './resolvers/index.js';

export function createApp(prisma: PrismaClient) {
  return createYoga({
    schema: createSchema({
      typeDefs,
      resolvers: buildResolvers(prisma) as any,
    }),
  });
}
