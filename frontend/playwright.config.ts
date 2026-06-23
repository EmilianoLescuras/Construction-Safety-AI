import { defineConfig, devices } from "@playwright/test";

// Frontend E2E tests. Assume the Docker compose stack (postgres + api +
// frontend) is already up at http://localhost:3000 and http://localhost:8000.
//
// Run:
//   npx playwright test
//   npx playwright test --ui      # interactive
//   npx playwright test --headed  # see the browser

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? "list" : "html",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
