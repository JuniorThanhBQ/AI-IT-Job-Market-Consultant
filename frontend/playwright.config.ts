import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  reporter: "list",
  use: {
    trace: "on-first-retry",
    baseURL: "http://localhost:3000/",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000/",
    reuseExistingServer: true,
  },
});
