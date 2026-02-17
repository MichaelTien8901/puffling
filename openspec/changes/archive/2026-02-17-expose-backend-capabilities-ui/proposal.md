## Why

The backend exposes key trading capabilities — risk analysis, portfolio optimization, live parameter adaptation, trade streaming, and broker account info — but none have frontend UI. Users must call raw API endpoints to access them. This change focuses on the highest-value features a trader needs daily: risk/position sizing before trades, portfolio management, account visibility, live trade feed, and adaptation controls.

## What Changes

- Add **Risk & Position Sizing** page: position sizing calculator (various methods), portfolio risk metrics (VaR, drawdown, concentration)
- Add **Portfolio** page: mean-variance weight optimization, performance tearsheet, factor-driven analysis (compute factors, PCA risk factors)
- Upgrade **Dashboard**: Account panel (cash, portfolio value), real-time trade feed via `/ws/trades`
- Upgrade **Optimize**: Live Adaptation management section (create/list/stop configs, view history)
- Upgrade **Backtest**: Progress bar via `/ws/backtest/{id}` during long-running backtests
- Integrate **ML model type selector** into existing Strategy/Backtest pages (not a standalone page)

## Capabilities

### New Capabilities
- `risk-ui`: Frontend page for position sizing calculator and portfolio risk metrics — consumes `/api/risk/*`
- `portfolio-ui`: Frontend page combining portfolio optimization, tearsheets, and factor analysis — consumes `/api/portfolio/*`, `/api/factors/compute`, `/api/factors/risk-factors`

### Modified Capabilities
- `trading-dashboard`: Add Account panel (broker cash/value via `/api/broker/account`), wire `/ws/trades` for real-time trade feed
- `optimization-ui`: Add Live Adaptation management section (create/list/stop/history via `/api/optimize/live/*`), add backtest progress bar via `/ws/backtest/{id}`

## Impact

- **Frontend**: 2 new pages (`/risk`, `/portfolio`), 3 modified pages (Dashboard, Optimize, Backtest)
- **Navigation**: Sidebar gains 2 new links (Risk, Portfolio)
- **Backend**: No changes — all routes and services already implemented
- **Dependencies**: No new dependencies — reuses existing Chart component, api client, and WebSocket hook
- **E2E Tests**: New Playwright tests for each new page; updated tests for modified pages
