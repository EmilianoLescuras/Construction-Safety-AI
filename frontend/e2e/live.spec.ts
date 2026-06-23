import { test, expect } from "@playwright/test";

test.describe("Live page", () => {
  test("renders Live monitor heading", async ({ page }) => {
    await page.goto("/live");
    await expect(
      page.getByRole("heading", { name: /live monitor/i }),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("pause/resume toggle works", async ({ page }) => {
    await page.goto("/live");
    const toggle = page.getByRole("button", { name: /pause|resume/i });
    if (await toggle.count()) {
      const before = (await toggle.textContent())?.toLowerCase() ?? "";
      await toggle.click();
      await expect(toggle).not.toHaveText(new RegExp(before, "i"));
    }
  });
});
