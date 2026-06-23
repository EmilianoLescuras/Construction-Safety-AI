import { test } from "@playwright/test";
import path from "path";

// These tests just take screenshots for the README. Run on demand:
//   npx playwright test e2e/screenshots.spec.ts
//
// Output: docs/screenshots/*.png

const OUT = path.resolve(__dirname, "../../docs/screenshots");

test.describe("Capture README screenshots", () => {
  test.use({ viewport: { width: 1440, height: 900 } });

  test("dashboard", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: path.join(OUT, "dashboard.png"), fullPage: true });
  });

  test("events list", async ({ page }) => {
    await page.goto("/events");
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: path.join(OUT, "events.png"), fullPage: true });
  });

  test("event detail", async ({ page }) => {
    await page.goto("/events/3");
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: path.join(OUT, "event_detail.png"), fullPage: true });
  });

  test("live monitor", async ({ page }) => {
    await page.goto("/live");
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: path.join(OUT, "live.png"), fullPage: true });
  });
});
