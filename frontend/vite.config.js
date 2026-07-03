import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    port: 8002,
    proxy: {
      '/api': 'http://localhost:8001',
      '/ws': { target: 'ws://localhost:8001', ws: true },
    },
  },
})
