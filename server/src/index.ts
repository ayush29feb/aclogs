import { createServer } from 'node:http';
import { PrismaClient } from '@prisma/client';
import { createApp } from './yoga.js';

const prisma = new PrismaClient();
const port = parseInt(process.env.PORT ?? '47322', 10);

const yoga = createApp(prisma);

const server = createServer(yoga);

server.listen(port, () => {
  console.log(`Gym GraphQL server running at http://localhost:${port}/graphql`);
});

async function shutdown() {
  await new Promise<void>((resolve, reject) =>
    server.close((err) => (err ? reject(err) : resolve()))
  );
  await prisma.$disconnect();
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
