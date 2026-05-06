import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: "./",   // 🔥 THIS is the key fix
  plugins: [react()],
})