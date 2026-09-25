import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// AutoFlow Pro: frontend on :5174, backend on :8000
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: { '/api': 'http://localhost:8000' },
  },
})
