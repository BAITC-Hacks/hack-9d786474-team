import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/tasks': 'http://127.0.0.1:8000', '/catalog': 'http://127.0.0.1:8000', '/teams': 'http://127.0.0.1:8000', '/proposals': 'http://127.0.0.1:8000', '/profiles': 'http://127.0.0.1:8000' } },
});
