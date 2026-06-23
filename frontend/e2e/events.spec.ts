import { test, expect, request } from "@playwright/test";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function seedEvent(): Promise<number> {
  const ctx = await request.newContext();
  const r = await ctx.post(`${API_URL}/events/batch`, {
    data: {
      source: "e2e-seed",
      events: [
        {
          rule: "vest",
          person_id: 1,
          frame: 30,
          first_seen_ts: 0.0,
          emitted_ts: 3.0,
          duration_seconds: 3.0,
          violation_class: "NO-Safety Vest",
          violation_conf: 0.9,
          person_bbox: [10, 10, 100, 200],
          violation_bbox: [20, 20, 80, 100],
        },
      ],
    },
  });
  expect(r.ok()).toBeTruthy();

  // Find the id by querying the list filtered on this source.
  const list = await ctx.get(`${API_URL}/events?limit=1`);
  const events = await list.json();
  expect(events.length).toBeGreaterThan(0);
  await ctx.dispose();
  return events[0].id;
}

test.describe("Events", () => {
  test("list page renders Events heading and a table", async ({ page }) => {
    await page.goto("/events");
    await expect(page.getByRole("heading", { name: "Events" })).toBeVisible({
      timeout: 10_000,
    });
    const table = page.locator("table");
    const empty = page.getByText(/no events/i);
    await expect(table.or(empty)).toBeVisible();
  });

  test("event detail page renders for a seeded event", async ({ page }) => {
    const id = await seedEvent();
    await page.goto(`/events/${id}`);
    await expect(
      page.getByRole("heading", { name: new RegExp(`Event #${id}`, "i") }),
    ).toBeVisible({ timeout: 10_000 });
  });
});
