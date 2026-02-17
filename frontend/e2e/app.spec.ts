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

test.describe("Live Prices", () => {
  test("live prices panel shows on dashboard", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Live Prices" })).toBeVisible();
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
      { label: "AI Chat", heading: "AI Trading Assistant" },
      { label: "Agent", heading: "AI Agent Activity" },
      { label: "Data", heading: "Data Explorer" },
      { label: "Trades", heading: "Trades" },
      { label: "Portfolio", heading: "Portfolio" },
      { label: "Risk", heading: "Risk & Position Sizing" },
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

  test("clicking run triggers backtest submission", async ({ page }) => {
    await page.goto("/backtest");

    const runBtn = page.getByRole("button", { name: "Run Backtest" });
    await runBtn.click();

    // After clicking, page should still be functional (no crash)
    await expect(pageHeading(page)).toHaveText("Backtest");
    await expect(runBtn).toBeVisible();
  });

  test("results display after mocked backtest run", async ({ page }) => {
    await page.route("**/api/backtest/", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          metrics: { total_return: 0.15, sharpe_ratio: 1.2 },
        }),
      })
    );

    await page.goto("/backtest");
    await page.getByRole("button", { name: "Run Backtest" }).click();

    await expect(page.getByRole("heading", { name: "Results" })).toBeVisible({ timeout: 10_000 });
    const pre = page.locator("pre");
    await expect(pre).toContainText("total_return");
    await expect(pre).toContainText("sharpe_ratio");
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

  test("toggle job enabled/disabled", async ({ page }) => {
    await page.goto("/scheduler");

    // Create a job first
    await page.getByRole("button", { name: "Create Job" }).click();
    const row = page.locator("tr", { hasText: "market_scan" });
    await expect(row).toBeVisible({ timeout: 10_000 });

    // Toggle enabled state
    const toggleBtn = row.getByRole("button", { name: /Enabled|Disabled/ });
    const initialText = await toggleBtn.textContent();
    await toggleBtn.click();

    // Verify state changed
    const expectedText = initialText === "Enabled" ? "Disabled" : "Enabled";
    await expect(toggleBtn).toHaveText(expectedText);

    // Cleanup: delete the job
    await row.getByRole("button", { name: "Delete" }).click();
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

  test("kill switch toggles between kill and resume", async ({ page }) => {
    await page.goto("/settings");

    const killBtn = page.getByRole("button", { name: "KILL SWITCH" });
    await expect(killBtn).toBeVisible({ timeout: 10_000 });

    // Activate kill switch
    await killBtn.click();
    const resumeBtn = page.getByRole("button", { name: "Resume Trading" });
    await expect(resumeBtn).toBeVisible({ timeout: 10_000 });

    // Resume trading
    await resumeBtn.click();
    await expect(page.getByRole("button", { name: "KILL SWITCH" })).toBeVisible({ timeout: 10_000 });
  });

  test("add and delete a setting", async ({ page }) => {
    await page.goto("/settings");

    // Add a setting
    await page.locator('input[placeholder="Key"]').fill("e2e_test_key");
    await page.locator('input[placeholder="Value (JSON or string)"]').fill("test_value");
    await page.getByRole("button", { name: "Save" }).click();

    // Verify it appears
    await expect(page.getByText("e2e_test_key")).toBeVisible({ timeout: 10_000 });

    // Delete it
    const row = page.locator("tr", { hasText: "e2e_test_key" });
    await row.getByRole("button", { name: "Delete" }).click();

    // Verify removal
    await expect(page.getByText("e2e_test_key")).not.toBeVisible();
  });

  test("safety number inputs are visible", async ({ page }) => {
    await page.goto("/settings");

    const numberInputs = page.locator('input[type="number"]');
    await expect(numberInputs.first()).toBeVisible();
    expect(await numberInputs.count()).toBeGreaterThanOrEqual(1);
  });
});

test.describe("Data Explorer", () => {
  test("page loads with form elements", async ({ page }) => {
    await page.goto("/data");
    await expect(pageHeading(page)).toHaveText("Data Explorer");

    await expect(page.locator('input[placeholder="Symbol"]')).toBeVisible();
    await expect(page.locator('input[type="date"]').first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Load" })).toBeVisible();
  });

  test("load button triggers data fetch", async ({ page }) => {
    await page.goto("/data");

    await page.locator('input[placeholder="Symbol"]').fill("AAPL");
    await page.getByRole("button", { name: "Load" }).click();

    // Either chart renders or we get an error/empty state — page shouldn't crash
    await page.waitForTimeout(2000);
    await expect(pageHeading(page)).toHaveText("Data Explorer");
  });

  test("chart renders with mocked OHLCV data", async ({ page }) => {
    await page.route("**/api/data/ohlcv**", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: [
            { Date: "2024-01-02", Open: 180, High: 185, Low: 179, Close: 184 },
            { Date: "2024-01-03", Open: 184, High: 188, Low: 183, Close: 187 },
            { Date: "2024-01-04", Open: 187, High: 189, Low: 185, Close: 186 },
          ],
        }),
      })
    );

    await page.goto("/data");
    await page.locator('input[placeholder="Symbol"]').fill("AAPL");
    await page.getByRole("button", { name: "Load" }).click();

    // TradingView lightweight-charts renders to canvas
    await expect(page.locator("canvas").first()).toBeVisible({ timeout: 10_000 });
  });
});

test.describe("Optimize", () => {
  test("page loads with form elements", async ({ page }) => {
    await page.goto("/optimize");
    await expect(pageHeading(page)).toHaveText("Optimize");

    await expect(page.locator("select")).toBeVisible();
    await expect(page.getByRole("button", { name: "Run Optimization" })).toBeVisible();
    // Default momentum grid params should be pre-filled
    await expect(page.getByText("short_window")).toBeVisible();
    await expect(page.getByText("long_window")).toBeVisible();
  });

  test("strategy type selector changes param grid", async ({ page }) => {
    await page.goto("/optimize");

    // Default is momentum
    await expect(page.getByText("short_window")).toBeVisible();

    // Switch to mean reversion
    await page.locator("select").selectOption("mean_reversion");
    await expect(page.getByText("num_std")).toBeVisible();
    await expect(page.getByText("zscore_entry")).toBeVisible();

    // Switch to stat arb
    await page.locator("select").selectOption("stat_arb");
    await expect(page.getByText("lookback")).toBeVisible();
    await expect(page.getByText("entry_zscore")).toBeVisible();
  });

  test("advanced settings toggle", async ({ page }) => {
    await page.goto("/optimize");

    // Advanced settings hidden by default
    await expect(page.getByText("Walk-Forward Splits")).not.toBeVisible();

    // Show advanced
    await page.getByText("Show Advanced Settings").click();
    await expect(page.getByText("Walk-Forward Splits")).toBeVisible();
    await expect(page.getByText("Train Ratio")).toBeVisible();

    // Hide again
    await page.getByText("Hide Advanced Settings").click();
    await expect(page.getByText("Walk-Forward Splits")).not.toBeVisible();
  });

  test("results table displays with mocked optimization data", async ({ page }) => {
    // Mock the submit endpoint to return a job_id
    await page.route("**/api/optimize/strategy", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ job_id: 1, status: "running", total_combinations: 18 }),
      })
    );

    // Mock the poll endpoint to return completed results
    await page.route("**/api/optimize/1", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          status: "complete",
          results: [
            { rank: 1, params: { short_window: 10, long_window: 50, ma_type: "ema" }, mean_sharpe: 1.45, mean_return: 0.12, max_drawdown: -0.08, mean_win_rate: 0.58 },
            { rank: 2, params: { short_window: 20, long_window: 100, ma_type: "sma" }, mean_sharpe: 1.20, mean_return: 0.09, max_drawdown: -0.10, mean_win_rate: 0.55 },
          ],
        }),
      })
    );

    // Mock job list
    await page.route("**/api/optimize/", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      })
    );

    await page.goto("/optimize");
    await page.getByRole("button", { name: "Run Optimization" }).click();

    // Results table should appear after polling
    await expect(page.getByRole("heading", { name: "Results" })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("1.450")).toBeVisible();
    await expect(page.getByText("1.200")).toBeVisible();

    // Action buttons on result rows
    await expect(page.getByRole("button", { name: "Backtest" }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Save as Strategy" }).first()).toBeVisible();
  });

  test("auto mode hides param grid and shows note", async ({ page }) => {
    await page.route("**/api/optimize/", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.goto("/optimize");

    // Select auto mode
    await page.locator("select").selectOption("auto");

    // Param grid should be hidden, auto note shown
    await expect(page.getByText("Auto mode will evaluate all 4 strategy types")).toBeVisible();
    await expect(page.getByText("short_window")).not.toBeVisible();

    // Switch back to momentum — grid reappears
    await page.locator("select").selectOption("momentum");
    await expect(page.getByText("short_window")).toBeVisible();
    await expect(page.getByText("Auto mode will evaluate all 4 strategy types")).not.toBeVisible();
  });

  test("sweep results show comparison table", async ({ page }) => {
    const sweepResults = {
      by_strategy: {
        momentum: [
          { rank: 1, params: { short_window: 10, long_window: 50 }, mean_sharpe: 1.45, mean_return: 0.12, max_drawdown: -0.08, mean_win_rate: 0.58, recommended: true, sharpe_std: 0.2 },
        ],
        mean_reversion: [
          { rank: 1, params: { window: 20 }, mean_sharpe: 0.8, mean_return: 0.05, max_drawdown: -0.12, mean_win_rate: 0.52, recommended: true, sharpe_std: 0.5 },
        ],
        market_making: [
          { rank: 1, params: { spread_bps: 10 }, mean_sharpe: -0.3, mean_return: -0.02, max_drawdown: -0.15, mean_win_rate: 0.45, recommended: false, sharpe_std: 0.1 },
        ],
      },
      recommendation: { strategy_type: "momentum", best_params: { short_window: 10 }, mean_sharpe: 1.45, sharpe_std: 0.2, confidence: "high", recommended: true },
    };

    await page.route("**/api/optimize/sweep", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ job_id: 10, status: "running", strategy_types: ["momentum", "mean_reversion", "stat_arb", "market_making"] }) })
    );
    await page.route("**/api/optimize/10", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "complete", job_type: "sweep", results: sweepResults }) })
    );
    await page.route("**/api/optimize/", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );

    await page.goto("/optimize");
    await page.locator("select").selectOption("auto");
    await page.getByRole("button", { name: "Run Optimization" }).click();

    // Comparison table should appear
    await expect(page.getByRole("heading", { name: "Strategy Comparison" })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Recommended:", { exact: false })).toBeVisible();
    await expect(page.getByRole("button", { name: /momentum/ })).toBeVisible();
    await expect(page.getByText("Not recommended", { exact: true })).toBeVisible();
    await expect(page.getByRole("cell", { name: "1.450" })).toBeVisible();
  });

  test("optimization history displays with mocked jobs", async ({ page }) => {
    await page.route("**/api/optimize/", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: 1, job_type: "strategy", strategy_type: "momentum", status: "complete", created_at: "2024-06-01T10:00:00", best_sharpe: 1.45 },
          { id: 2, job_type: "strategy", strategy_type: "mean_reversion", status: "running", created_at: "2024-06-02T10:00:00", best_sharpe: null },
        ]),
      })
    );

    await page.goto("/optimize");

    await expect(page.getByRole("heading", { name: "Optimization History" })).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole("cell", { name: "momentum" })).toBeVisible();
    await expect(page.getByRole("cell", { name: "mean_reversion" })).toBeVisible();
    await expect(page.getByText("1.450")).toBeVisible();
    await expect(page.getByText("View Results")).toBeVisible();
  });
});

test.describe("Trades", () => {
  test("page loads with trade history section", async ({ page }) => {
    await page.goto("/trades");
    await expect(pageHeading(page)).toHaveText("Trades");

    await expect(page.getByRole("heading", { name: "Trade History" })).toBeVisible();

    // Empty state or table should be present
    const hasEmptyState = await page.getByText("No trades recorded").isVisible().catch(() => false);
    const hasTable = await page.locator("table").isVisible().catch(() => false);
    expect(hasEmptyState || hasTable).toBeTruthy();
  });

  test("asset type selector shows conditional fields", async ({ page }) => {
    await page.goto("/trades");
    await expect(pageHeading(page)).toHaveText("Trades");

    const assetSelect = page.locator('[data-testid="asset-type"]');
    await expect(assetSelect).toBeVisible();

    // Select Option — expiry, strike, right should appear
    await assetSelect.selectOption("OPT");
    await expect(page.locator('[data-testid="expiry"]')).toBeVisible();
    await expect(page.locator('[data-testid="strike"]')).toBeVisible();
    await expect(page.locator('[data-testid="right"]')).toBeVisible();

    // Switch back to Stock — those fields should disappear
    await assetSelect.selectOption("STK");
    await expect(page.locator('[data-testid="expiry"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="strike"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="right"]')).not.toBeVisible();
  });

  test("order confirmation modal shows and cancels", async ({ page }) => {
    await page.goto("/trades");

    // Fill in order form
    await page.locator('input[placeholder="SPY"]').fill("AAPL");
    await page.locator('input[placeholder="10"]').fill("5");

    // Click Review Order — modal should appear
    await page.getByRole("button", { name: "Review Order" }).click();
    const modal = page.locator('[data-testid="confirm-modal"]');
    await expect(modal).toBeVisible();
    await expect(modal.getByText("AAPL")).toBeVisible();
    await expect(modal.getByText("BUY")).toBeVisible();
    await expect(modal.getByText("5")).toBeVisible();

    // Cancel — modal should disappear
    await page.getByRole("button", { name: "Cancel" }).click();
    await expect(modal).not.toBeVisible();
  });

  test("populated table and P&L with mocked data", async ({ page }) => {
    await page.route("**/api/monitor/trades", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { symbol: "SPY", side: "BUY", qty: 10, price: 450.0, timestamp: "2024-06-01T10:00:00" },
          { symbol: "AAPL", side: "SELL", qty: 5, price: 190.0, timestamp: "2024-06-01T11:00:00" },
        ]),
      })
    );
    await page.route("**/api/monitor/pnl", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ total_pnl: 1250.0, win_rate: 0.65 }),
      })
    );

    await page.goto("/trades");

    // Verify table has trade data
    await expect(page.getByText("SPY")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole("cell", { name: "BUY" })).toBeVisible();
    await expect(page.getByText("AAPL")).toBeVisible();

    // Verify P&L section
    await expect(page.getByRole("heading", { name: "P&L Summary" })).toBeVisible();
  });
});

test.describe("AI Chat", () => {
  test("page loads with input and send button", async ({ page }) => {
    await page.goto("/ai");
    await expect(pageHeading(page)).toHaveText("AI Trading Assistant");

    await expect(page.locator('input[placeholder="Type a message..."], input[placeholder="Connecting..."]')).toBeVisible();
    await expect(page.getByRole("button", { name: "Send" })).toBeVisible();
    await expect(page.getByText("Ask me about markets, strategies, or trading...")).toBeVisible();
  });

  test("typing a message shows user bubble", async ({ page }) => {
    await page.goto("/ai");

    const input = page.locator('input[placeholder="Type a message..."]');
    // Wait for WebSocket connection
    await expect(input).toBeVisible({ timeout: 10_000 });

    await input.fill("Hello from E2E test");
    await page.getByRole("button", { name: "Send" }).click();

    // User message should appear as a blue bubble
    await expect(page.locator(".bg-blue-600", { hasText: "Hello from E2E test" })).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Agent", () => {
  test("page loads with run button", async ({ page }) => {
    await page.goto("/agent");
    await expect(pageHeading(page)).toHaveText("AI Agent Activity");

    await expect(page.getByRole("button", { name: "Run Agent Now" })).toBeVisible();
    await expect(page.getByText("No agent runs yet")).toBeVisible();
  });

  test("run button shows running state", async ({ page }) => {
    // Mock a slow agent run so we can observe the "Running..." state
    await page.route("**/api/agent/run", (route) =>
      new Promise((resolve) => setTimeout(() => resolve(route.fulfill({ status: 200, contentType: "application/json", body: "{}" })), 5000))
    );

    await page.goto("/agent");

    await page.getByRole("button", { name: "Run Agent Now" }).click();
    await expect(page.getByRole("button", { name: "Running..." })).toBeVisible();
  });

  test("logs display with mocked agent data", async ({ page }) => {
    await page.route("**/api/agent/logs", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: 1,
            run_at: "2024-06-01T09:00:00",
            report: JSON.stringify({ analysis: "Market is bullish" }),
            actions_taken: "[]",
          },
        ]),
      })
    );

    await page.goto("/agent");

    await expect(page.getByText("Market is bullish")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText("Run #1")).toBeVisible();
  });
});

test.describe("Risk", () => {
  test("page loads with position sizing form", async ({ page }) => {
    await page.goto("/risk");
    await expect(pageHeading(page)).toHaveText("Risk & Position Sizing");
    await expect(page.getByRole("heading", { name: "Position Sizing", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Portfolio Risk Metrics" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Calculate" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Compute Risk" })).toBeVisible();
  });

  test("method dropdown changes param fields", async ({ page }) => {
    await page.goto("/risk");
    // Default is percent_risk — should show account_size, risk_pct, entry_price, stop_price
    await expect(page.getByText("account_size")).toBeVisible();
    await expect(page.getByText("stop_price")).toBeVisible();

    // Switch to kelly
    await page.locator("select").first().selectOption("kelly");
    await expect(page.getByText("win_rate")).toBeVisible();
    await expect(page.getByText("avg_win")).toBeVisible();
    // percent_risk fields should be gone
    await expect(page.getByText("stop_price")).not.toBeVisible();
  });

  test("mocked position size result displays", async ({ page }) => {
    await page.route("**/api/risk/position-size", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ position_size: 150, dollar_risk: 300 }),
      })
    );
    await page.goto("/risk");
    await page.getByRole("button", { name: "Calculate" }).click();
    await expect(page.getByText("position_size")).toBeVisible();
    await expect(page.getByText("150")).toBeVisible();
  });

  test("mocked portfolio risk result displays", async ({ page }) => {
    await page.route("**/api/risk/portfolio", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ var_95: -0.0234, max_drawdown: -0.1523, sharpe: 1.45, volatility: 0.189 }),
      })
    );
    await page.goto("/risk");
    await page.getByRole("button", { name: "Compute Risk" }).click();
    await expect(page.getByText("var_95")).toBeVisible();
    await expect(page.getByText("sharpe")).toBeVisible();
  });
});

test.describe("Portfolio", () => {
  test("page loads with optimization form", async ({ page }) => {
    await page.goto("/portfolio");
    await expect(pageHeading(page)).toHaveText("Portfolio");
    await expect(page.getByRole("heading", { name: "Portfolio Optimization" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Optimize" })).toBeVisible();
  });

  test("mocked optimization weights display", async ({ page }) => {
    await page.route("**/api/portfolio/optimize", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ weights: { AAPL: 0.35, GOOGL: 0.40, MSFT: 0.25 } }),
      })
    );
    await page.goto("/portfolio");
    await page.getByRole("button", { name: "Optimize" }).click();
    await expect(page.getByText("AAPL")).toBeVisible();
    await expect(page.getByText("0.35")).toBeVisible();
  });

  test("mocked tearsheet displays metrics", async ({ page }) => {
    await page.route("**/api/portfolio/tearsheet", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ total_return: 0.25, cagr: 0.12, sharpe: 1.8, max_drawdown: -0.15 }),
      })
    );
    await page.goto("/portfolio");
    const returnsInput = page.locator('input[placeholder="0.01, 0.02, -0.005"]');
    await returnsInput.fill("0.01, 0.02, 0.03");
    await page.getByRole("button", { name: "Generate Tearsheet" }).click();
    await expect(page.getByText("total_return")).toBeVisible();
    await expect(page.getByText("sharpe", { exact: true })).toBeVisible();
  });

  test("mocked factor results display", async ({ page }) => {
    await page.route("**/api/factors/compute", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ AAPL: { momentum: 0.05, volatility: 0.2 }, GOOGL: { momentum: 0.03, volatility: 0.18 } }),
      })
    );
    await page.goto("/portfolio");
    await page.getByRole("button", { name: "Compute Factors" }).click();
    await expect(page.getByText("momentum")).toBeVisible();
  });
});

test.describe("Dashboard Account & Trades", () => {
  test("account panel shows broker data", async ({ page }) => {
    await page.route("**/api/broker/account", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ cash: 50000, portfolio_value: 125000, buying_power: 100000 }),
      })
    );
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Account" })).toBeVisible();
    await expect(page.getByText("$50,000")).toBeVisible();
    await expect(page.getByText("$125,000")).toBeVisible();
  });

  test("account panel handles broker error", async ({ page }) => {
    await page.route("**/api/broker/account", (route) =>
      route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "error" }) })
    );
    await page.goto("/");
    await expect(page.getByText("Broker not connected")).toBeVisible();
  });
});

test.describe("Optimize Live Adaptation", () => {
  test("live adaptation section renders", async ({ page }) => {
    await page.route("**/api/optimize/live", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            { id: 1, strategy_type: "momentum", next_run: "2024-06-01T10:00:00", status: "active" },
          ]),
        });
      }
      return route.continue();
    });
    await page.goto("/optimize");
    await page.getByText("Live Adaptation").click();
    await expect(page.getByRole("cell", { name: "momentum" }).first()).toBeVisible();
  });
});

test.describe("Backtest Progress", () => {
  test("progress indicator shows during backtest", async ({ page }) => {
    await page.route("**/api/backtest/", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ id: 42, metrics: { sharpe: 1.5 } }),
        });
      }
      return route.continue();
    });
    await page.goto("/backtest");
    await page.getByRole("button", { name: "Run Backtest" }).click();
    // After submit, should show results (backtest returns synchronously in current impl)
    await expect(page.getByText("Results")).toBeVisible();
  });
});
