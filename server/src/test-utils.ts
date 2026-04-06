import { createYoga, createSchema } from 'graphql-yoga';
import { PrismaClient } from '@prisma/client';
import { typeDefs } from './schema.js';
import { buildResolvers } from './resolvers/index.js';

export function createTestYoga(prisma: PrismaClient) {
  return createYoga({
    schema: createSchema({
      typeDefs,
      resolvers: buildResolvers(prisma) as any,
    }),
    logging: false,
  });
}

export async function gql(
  yoga: ReturnType<typeof createYoga>,
  query: string,
  variables?: Record<string, unknown>
) {
  const res = await yoga.fetch('http://localhost/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  return res.json() as Promise<{ data: Record<string, unknown>; errors?: unknown[] }>;
}
