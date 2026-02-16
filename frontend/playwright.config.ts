import { defineConfig } from "@playwright/test";

// In Docker, use service names; locally, use localhost
const baseURL = process.env.CI ? "http://frontend:3000" : "http://localhost:3000";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 1,
  use: {
    baseURL,
    headless: true,
  },
});
