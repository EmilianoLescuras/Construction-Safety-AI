import { test, expect } from "@playwright/test";

test.describe("Events", () => {
  test("list page renders Events heading and a table", async ({ page }) => {
    await page.goto("/events");
    await expect(page.getByRole("heading", { name: "Events" })).toBeVisible({
      timeout: 10_000,
    });
    // Either the table renders (with seed data) or the empty state shows.
    const table = page.locator("table");
    const empty = page.getByText(/no events/i);
    await expect(table.or(empty)).toBeVisible();
  });

  test("event detail page renders evidence images", async ({ page }) => {
    await page.goto("/events/3");
    await expect(page.getByRole("heading", { name: /Event #3/i })).toBeVisible({
      timeout: 10_000,
    });

    // The evidence image(s) must successfully load (naturalWidth > 0).
    const imgs = page.locator("img");
    await expect(imgs.first()).toBeVisible();
    const naturalWidth = await imgs.first().evaluate(
      (el) => (el as HTMLImageElement).naturalWidth,
    );
    expect(naturalWidth).toBeGreaterThan(0);
  });
});
