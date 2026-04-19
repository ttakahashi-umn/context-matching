import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const fileEnv = loadEnv(mode, process.cwd(), "");
  // Docker Compose 等は process.env に渡す。loadEnv は主に .env ファイル用。
  const target =
    process.env.VITE_API_PROXY_TARGET ??
    fileEnv.VITE_API_PROXY_TARGET ??
    "http://127.0.0.1:8000";

  return {
    plugins: [react(), tailwindcss()],
    server: {
      host: "0.0.0.0",
      port: 5173,
      // Docker の bind mount では inotify が効かないことがあるためポーリングを有効化可能
      watch:
        process.env.CHOKIDAR_USEPOLLING === "true" ? { usePolling: true, interval: 300 } : undefined,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  };
});
