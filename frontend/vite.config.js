import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: "./",   // 🔥 VERY IMPORTANT (fixes Darwin proxy issue)
  plugins: [react()],
})