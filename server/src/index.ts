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

process.on('SIGTERM', async () => {
  await prisma.$disconnect();
  server.close();
});
