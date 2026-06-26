import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { federation } from "@module-federation/vite";
import path from "path";
import { fileURLToPath } from "url";
import tailwindcss from "@tailwindcss/vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const isTesting = !!process.env.VITEST;

export default defineConfig({
  server: {
    fs: {
      allow: [".", "../shared"],
    },
    proxy: {
      "/ui/cryptpad": {
        target: "http://localhost:4174",
        rewrite: (path) => path.replace(/^\/ui\/cryptpad/, ""),
      },
    },
  },
  build: {
    target: "chrome89",
    emptyOutDir: true,
    rollupOptions: {
      preserveEntrySignatures: "exports-only",
    },
  },
  plugins: [
    ...(isTesting
      ? []
      : [
          federation({
            filename: "remoteEntry.js",
            name: "cryptpad-integration",
            exposes: {
              "./remote-ui": "./src/App.tsx",
            },
            remotes: {},
            shared: {
              react: {
                requiredVersion: "18.3.1",
                singleton: true,
              },
              i18next: {
                requiredVersion: "25.6.2",
                singleton: true,
              },
              "react-i18next": {
                requiredVersion: "16.3.3",
                singleton: true,
              },
              "@tanstack/react-router": {
                requiredVersion: "1.135.2",
                singleton: true,
              },
            },
            runtime: "@module-federation/enhanced/runtime",
          }),
        ]),
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  define: {
    __USE_GLOBAL_CSS__: JSON.stringify(
      process.env.VITE_USE_GLOBAL_CSS === "true",
    ),
  },
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
