import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import dns from 'dns';

// Disable Node.js DNS caching to handle Docker container IP changes
dns.setDefaultResultOrder('ipv4first');

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      // In Docker/production, this proxies to the backend service on the internal network
      // In development on localhost, this proxies to localhost:8000
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));