## 1. Navigation

- [x] 1.1 Add "Portfolio" and "Risk" links to sidebar `navItems` in `Sidebar.tsx`

## 2. Risk & Position Sizing Page

- [x] 2.1 Create `/risk/page.tsx` with position sizing form (method dropdown, dynamic param fields, submit)
- [x] 2.2 Add portfolio risk metrics panel (symbols, weights, date range inputs, results table with VaR/drawdown/Sharpe/volatility)
- [x] 2.3 Add Playwright E2E tests for Risk page (form renders, method switching, mocked position size result, mocked portfolio risk result)

## 3. Portfolio Page

- [x] 3.1 Create `/portfolio/page.tsx` with portfolio optimization form (symbols, date range, method, submit) and weights result table
- [x] 3.2 Add performance tearsheet panel (returns input, generate button, metrics as key-value cards)
- [x] 3.3 Add factor analysis panel (symbols, date range, compute factors table, PCA risk factors ranked list)
- [x] 3.4 Add Playwright E2E tests for Portfolio page (optimization form, mocked weights result, mocked tearsheet, mocked factor results)

## 4. Dashboard Upgrades

- [x] 4.1 Add Account summary panel to dashboard (fetch `GET /api/broker/account`, display cash/portfolio value/buying power as stat cards, handle broker-not-connected)
- [x] 4.2 Add Recent Trades panel with `/ws/trades` WebSocket feed (last 10 trades, symbol/side/qty/price/timestamp, disconnected indicator)
- [x] 4.3 Add Playwright E2E tests for new dashboard panels (mocked account data, mocked trade feed)

## 5. Optimize Page Upgrades

- [x] 5.1 Add collapsible Live Adaptation section (list active adaptations table from `GET /api/optimize/live`, create form, stop button per row)
- [x] 5.2 Add adaptation history expandable view per row (`GET /api/optimize/live/{id}/history`, event list with trigger/params/status)
- [x] 5.3 Add Playwright E2E tests for Live Adaptation section (mocked adaptation list, create, stop, history)

## 6. Backtest Progress Indicator

- [x] 6.1 Add WebSocket-driven progress indicator to Backtest page (connect to `/ws/backtest/{id}` after submit, show progress bar, fallback to static "Running...")
- [x] 6.2 Add Playwright E2E test for backtest progress indicator (mocked WebSocket messages)
