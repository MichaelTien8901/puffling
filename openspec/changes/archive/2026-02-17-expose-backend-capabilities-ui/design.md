## Context

The Puffling backend wraps Puffin's full capability set with implemented routes and services for risk analysis, portfolio optimization, factor analysis, live adaptation, trade streaming, and broker account info. None of these have frontend UI.

The frontend follows a consistent pattern: `"use client"` pages using `api.get/post` from `@/lib/api`, `useWebSocket` hook for real-time data, white card panels in responsive grids, and the shared `Chart` component for visualizations.

## Goals / Non-Goals

**Goals:**
- Expose the highest-value backend capabilities through 2 new pages and 3 page upgrades
- Follow established frontend patterns exactly (no new abstractions or dependencies)
- Add Playwright E2E tests with mocked API responses for every change

**Non-Goals:**
- No backend changes — all routes and services already exist
- No standalone Models page — integrate model type selector into existing Strategy/Backtest flows
- No standalone Factors page — fold factor analysis into Portfolio page
- No standalone Clustering page — niche feature, defer
- No new visualization libraries — HTML tables and existing Chart component only

## Decisions

### 1. Two new pages, not four

**Risk & Position Sizing** (`/risk`) and **Portfolio** (`/portfolio`) are the two new pages. ML models and factor analysis are integrated into existing pages rather than standalone.

**Rationale:** Traders use risk/sizing before every trade and review portfolio weekly. Model training and factor browsing are better triggered from context (strategy creation, portfolio review) than from isolated pages.

### 2. Portfolio page combines optimization + tearsheet + factors

One page with three sections:
- **Optimize Weights** — form with symbols + method, results as weight table
- **Performance Tearsheet** — upload/select returns, render metrics as key-value cards
- **Factor Analysis** — compute factors for a symbol set, show as table; PCA risk factors as ranked list

**Alternative considered:** Separate pages for each. Rejected — all three answer "how is my portfolio doing?" and benefit from shared context.

### 3. Risk page: two panels

- **Position Sizing** — select method (fixed, percent-risk, Kelly, volatility), input parameters, get recommended size
- **Portfolio Risk** — input symbols or use current positions, get VaR, max drawdown, Sharpe, correlation matrix

### 4. Dashboard upgrades: Account panel + trade feed

- **Account panel**: `api.get("/api/broker/account")` on mount, show cash, portfolio value, buying power as stat cards
- **Trade feed**: connect `useWebSocket("/ws/trades")`, show last 10 trades as a scrolling list below Account

### 5. Optimize page: Live Adaptation section

Add a collapsible section at bottom of Optimize page:
- **Active Adaptations** table: list from `GET /api/optimize/live`, each row has stop button (`DELETE`)
- **Create Adaptation** form: strategy selector, regime parameters, submit to `POST /api/optimize/live`
- **History** expandable per-adaptation: `GET /api/optimize/live/{id}/history`

### 6. Backtest progress bar

After `POST /api/backtest/`, connect to `/ws/backtest/{id}`. Show indeterminate progress bar while connected, replace with results on completion. Fall back to polling if WebSocket fails.

### 7. Sidebar: add Risk and Portfolio links

Insert into `navItems` array in `Sidebar.tsx`:
- Portfolio (after Trades)
- Risk (after Portfolio)

Total: 12 sidebar items — still manageable for a power-user app.

### 8. E2E tests: follow existing mock pattern

Each new page gets 3-4 Playwright tests using `page.route()` mocks. Modified pages get 1-2 additional tests for new panels. Matches the style of the existing 33 tests.

## Risks / Trade-offs

- **Account panel shows stale data on paper trading** → Acceptable; refresh on page load is sufficient. Add a manual refresh button.
- **Backtest WebSocket message format undocumented** → Read `backtest_ws.py` during implementation to determine message shape. Worst case, show "Running..." without percentage.
- **Tearsheet output structure TBD** → Render as key-value table initially; can add charts in a follow-up.
- **12 sidebar items** → Acceptable for now. Can group with section headers in a future change if needed.
