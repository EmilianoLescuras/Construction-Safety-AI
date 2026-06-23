import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test("renders all four KPI cards", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible({
      timeout: 10_000,
    });

    for (const label of [
      "Total events",
      "Total dispatches",
      "Dispatch success",
      "Rules triggered",
    ]) {
      await expect(page.getByText(label, { exact: true })).toBeVisible();
    }
  });

  test("renders 'Violations by rule' chart card", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText(/violations by rule/i)).toBeVisible({
      timeout: 10_000,
    });
  });

  test("links to events list", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /events/i }).first().click();
    await expect(page).toHaveURL(/\/events/);
  });
});
