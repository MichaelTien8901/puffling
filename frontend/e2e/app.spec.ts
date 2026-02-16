import { test, expect } from "@playwright/test";

// The sidebar has an h1 "Puffling", so target the main content h1
const pageHeading = (page: import("@playwright/test").Page) =>
  page.locator("main h1");

test.describe("Dashboard", () => {
  test("loads and shows panels", async ({ page }) => {
    await page.goto("/");
    await expect(pageHeading(page)).toHaveText("Dashboard");
    await expect(page.getByRole("heading", { name: "Portfolio", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Active Strategies" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Recent Trades" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Recent Alerts" })).toBeVisible();
  });
});

test.describe("Navigation", () => {
  test("sidebar links navigate to correct pages", async ({ page }) => {
    await page.goto("/");

    const routes = [
      { label: "Strategies", heading: "Strategies" },
      { label: "Backtest", heading: "Backtest" },
      { label: "Scheduler", heading: "Scheduler" },
      { label: "Settings", heading: "Settings" },
      { label: "Dashboard", heading: "Dashboard" },
    ];

    for (const { label, heading } of routes) {
      await page.getByRole("link", { name: label }).click();
      await expect(pageHeading(page)).toHaveText(heading);
    }
  });
});

test.describe("Strategy CRUD", () => {
  test("create and delete a strategy", async ({ page }) => {
    await page.goto("/strategies");
    await expect(pageHeading(page)).toHaveText("Strategies");

    // Create
    await page.locator('input[placeholder="Name"]').fill("E2E Test Strategy");
    await page.getByRole("button", { name: "Create" }).click();

    // Verify it appears (wait for API response)
    await expect(page.getByText("E2E Test Strategy")).toBeVisible({ timeout: 10_000 });

    // Delete
    const row = page.locator("tr", { hasText: "E2E Test Strategy" });
    await row.getByRole("button", { name: "Delete" }).click();

    // Verify it's gone
    await expect(page.getByText("E2E Test Strategy")).not.toBeVisible();
  });
});

test.describe("Backtest", () => {
  test("form renders with fields and run button", async ({ page }) => {
    await page.goto("/backtest");
    await expect(pageHeading(page)).toHaveText("Backtest");

    await expect(page.getByText("Strategy", { exact: true })).toBeVisible();
    await expect(page.getByText("Symbols", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Run Backtest" })).toBeVisible();
  });
});

test.describe("Scheduler", () => {
  test("create and delete a job", async ({ page }) => {
    await page.goto("/scheduler");
    await expect(pageHeading(page)).toHaveText("Scheduler");

    // Create job with defaults
    await page.getByRole("button", { name: "Create Job" }).click();

    // Verify it appears in the table
    const row = page.locator("tr", { hasText: "market_scan" });
    await expect(row).toBeVisible({ timeout: 10_000 });

    // Delete
    await row.getByRole("button", { name: "Delete" }).click();

    // Verify it's gone
    await expect(row).not.toBeVisible();
  });
});

test.describe("Settings & Safety", () => {
  test("page loads with safety controls", async ({ page }) => {
    await page.goto("/settings");
    await expect(pageHeading(page)).toHaveText("Settings");
    await expect(page.getByRole("heading", { name: "Safety Controls" })).toBeVisible();
    await expect(page.getByText("Kill Switch", { exact: true })).toBeVisible();
  });

  test("kill switch button is visible", async ({ page }) => {
    await page.goto("/settings");

    const killBtn = page.getByRole("button", { name: /KILL SWITCH|Resume Trading/ });
    await expect(killBtn).toBeVisible();
  });
});
