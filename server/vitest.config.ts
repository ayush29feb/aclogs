import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    env: {
      DATABASE_URL: `file:${path.resolve(__dirname, '../data/gym.db')}`,
    },
  },
});
