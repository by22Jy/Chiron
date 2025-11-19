import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { resolve } from "path"

export default defineConfig({
  plugins: [vue()],
  server: { port: 5173, host: '127.0.0.1' },
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
})


