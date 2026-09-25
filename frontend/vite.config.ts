import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: /api → FastAPI on :8000. Prod: set VITE_API_URL to the deployed backend.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
