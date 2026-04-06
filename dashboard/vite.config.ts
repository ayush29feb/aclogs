import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import relay from 'vite-plugin-relay';

export default defineConfig({
  plugins: [react(), relay],
  server: {
    port: 47323,
    proxy: {
      '/graphql': 'http://localhost:47322',
    },
  },
});
