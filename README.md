# Puffling - AI-Powered Algorithmic Trading App

A personal AI-powered trading application built on top of [Puffin](https://github.com/MichaelTien8901/puffin) — the algorithmic trading library.

## Architecture

- **Backend**: FastAPI — REST/WebSocket API wrapping Puffin's trading modules
- **Frontend**: Next.js + React — Rich trading dashboard with real-time charts
- **Desktop**: Tauri — Lightweight native app for Linux/Windows

## Project Structure

```
puffling/
├── backend/         # FastAPI application
│   ├── api/         # REST routes & WebSocket handlers
│   ├── services/    # Thin wrappers around Puffin modules
│   ├── models/      # SQLAlchemy ORM models
│   └── core/        # Config, database, dependencies
├── frontend/        # Next.js application
│   └── src/
├── desktop/         # Tauri desktop shell
└── pyproject.toml
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (recommended)
- Rust toolchain (for Tauri desktop builds)
- [Puffin](https://github.com/MichaelTien8901/puffin) library cloned at `~/projects/puffin`

## Quick Start (Docker)

```bash
docker compose up -d backend frontend    # Start backend + frontend
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
docker compose down                       # Stop all services
```

## Setup (Standalone)

```bash
# Install Puffin as editable dependency
pip install -e ~/projects/puffin

# Install Puffling backend + dev dependencies
pip install -e ".[dev]"

# Run backend
uvicorn backend.main:app --reload

# Install and run frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Testing

### Backend unit tests (62 tests)

**Docker (recommended)** — handles Puffin installation automatically:
```bash
docker compose run --rm test-backend
```

Run a specific test file:
```bash
docker compose run --rm test-backend sh -c \
  "uv pip install --system --no-build-isolation /puffin && pytest tests/test_optimizer.py -v"
```

**Standalone** — requires Puffin and dev deps installed locally:
```bash
pytest tests/ -v
```

### Frontend E2E tests (45 tests)

Requires backend + frontend running:
```bash
# Start services
docker compose up -d backend frontend

# First time: install Playwright browsers
cd frontend
npx playwright install --with-deps

# Run all E2E tests
npx playwright test --reporter=list

# Run a specific test by name
npx playwright test --reporter=list -g "kill switch"
```

### Test inventory

#### Backend tests (62) — `docker compose run --rm test-backend`

| # | File | Test | Description |
|---|------|------|-------------|
| 1 | test_api.py | test_health | Health endpoint returns ok |
| 2 | test_api.py | test_settings_crud | Create, read, delete settings |
| 3 | test_api.py | test_strategies_crud | Create, read, delete strategies |
| 4 | test_api.py | test_model_types | Model type listing |
| 5 | test_api.py | test_unknown_route | 404 for unknown routes |
| 6 | test_autonomous.py | test_scheduler_crud | Scheduler job create/delete |
| 7 | test_autonomous.py | test_portfolio_goals_crud | Portfolio goal create/delete |
| 8 | test_autonomous.py | test_alerts_crud | Alert config create/delete |
| 9 | test_autonomous.py | test_safety_controls | Kill switch and safety settings |
| 10 | test_autonomous.py | test_safety_service_can_trade | Safety service trade gating |
| 11 | test_broker_multi_asset.py | test_submit_options_order | Options order with expiry, strike, right |
| 12 | test_broker_multi_asset.py | test_submit_futures_order | Futures order with expiry, multiplier |
| 13 | test_broker_multi_asset.py | test_submit_forex_order | Forex order with pair_currency |
| 14 | test_broker_multi_asset.py | test_submit_non_us_stock_order | Non-US stock with exchange, currency |
| 15 | test_broker_multi_asset.py | test_simple_stock_order_unchanged | Plain stock order backward compat |
| 16 | test_broker_multi_asset.py | test_confirm_options_order_uses_contract_spec | Confirm routes to submit_order_with_spec |
| 17 | test_broker_multi_asset.py | test_confirm_stock_order_uses_submit_order | Confirm routes to submit_order for stocks |
| 18 | test_broker_multi_asset.py | test_needs_contract_spec_logic | _needs_contract_spec detection logic |
| 19 | test_e2e.py | test_app_starts_and_health | App startup and health check |
| 20 | test_e2e.py | test_full_strategy_flow | Strategy create → backtest flow |
| 21 | test_e2e.py | test_settings_roundtrip | Settings set → get → delete |
| 22 | test_e2e.py | test_model_types_available | ML model types available |
| 23 | test_e2e.py | test_factor_library_available | Factor library accessible |
| 24 | test_live_adaptation.py | test_volatility_ratio_normal | Normal volatility ratio calculation |
| 25 | test_live_adaptation.py | test_volatility_ratio_insufficient_data | Volatility with insufficient data |
| 26 | test_live_adaptation.py | test_trend_strength | Uptrend strength detection |
| 27 | test_live_adaptation.py | test_trend_strength_downtrend | Downtrend strength detection |
| 28 | test_live_adaptation.py | test_detect_regime_high_volatility | High volatility regime detection |
| 29 | test_live_adaptation.py | test_detect_regime_no_change | No regime change detection |
| 30 | test_live_adaptation.py | test_cap_params_within_limits | Params within safety limits |
| 31 | test_live_adaptation.py | test_cap_params_exceeds_limits | Params exceeding safety limits |
| 32 | test_live_adaptation.py | test_cap_params_non_numeric | Non-numeric param capping |
| 33 | test_live_adaptation.py | test_cooldown_check_no_events | Cooldown with no prior events |
| 34 | test_live_adaptation.py | test_cooldown_check_active | Active cooldown period |
| 35 | test_live_adaptation.py | test_cooldown_check_expired | Expired cooldown period |
| 36 | test_live_adaptation.py | test_create_adaptation | Create adaptation config |
| 37 | test_live_adaptation.py | test_list_adaptations | List adaptation configs |
| 38 | test_live_adaptation.py | test_stop_adaptation | Stop running adaptation |
| 39 | test_live_adaptation.py | test_stop_nonexistent_adaptation | Stop nonexistent adaptation |
| 40 | test_live_adaptation.py | test_adaptation_history_empty | Empty adaptation history |
| 41 | test_live_adaptation.py | test_adaptation_history_not_found | Adaptation history not found |
| 42 | test_optimizer.py | test_default_grids_exist | Default param grids for all 4 strategies |
| 43 | test_optimizer.py | test_grid_size_validation | Rejects grids > 500 combinations |
| 44 | test_optimizer.py | test_data_length_validation | Rejects insufficient data length |
| 45 | test_optimizer.py | test_expand_grid | Grid expansion to parameter combos |
| 46 | test_optimizer.py | test_default_grid_sizes_within_limit | All default grids under limit |
| 47 | test_optimizer.py | test_list_jobs_empty | Empty job list returns [] |
| 48 | test_optimizer.py | test_get_job_not_found | 404 for missing job |
| 49 | test_optimizer.py | test_submit_strategy_optimization | Submit optimization returns job_id |
| 50 | test_optimizer.py | test_submit_with_oversized_grid | 400 for oversized grid |
| 51 | test_optimizer.py | test_cancel_nonexistent_job | 404 for cancelling missing job |
| 52 | test_optimizer.py | test_list_jobs_after_submit | Job appears in list after submit |
| 53 | test_optimizer.py | test_build_recommendation | Build strategy recommendation |
| 54 | test_optimizer.py | test_build_recommendation_low_confidence | Low confidence recommendation |
| 55 | test_optimizer.py | test_build_recommendation_negative_sharpe | Negative Sharpe recommendation |
| 56 | test_optimizer.py | test_build_recommendation_empty | Empty results recommendation |
| 57 | test_optimizer.py | test_submit_sweep | Submit strategy sweep |
| 58 | test_optimizer.py | test_sweep_job_in_list | Sweep job appears in list |
| 59 | test_services.py | test_settings_service | SettingsService CRUD operations |
| 60 | test_services.py | test_model_service_list_types | ModelService type listing |
| 61 | test_strategy_runner.py | test_activate_deactivate | Strategy activation toggle |
| 62 | test_strategy_runner.py | test_auto_trade_blocked_by_kill_switch | Kill switch blocks auto-trade |

#### Frontend E2E tests (45) — `cd frontend && npx playwright test --reporter=list`

Requires: `docker compose up -d backend frontend`

| # | Suite | Test | Description |
|---|-------|------|-------------|
| 1 | Dashboard | loads and shows panels | Page heading + panel headings |
| 2 | Live Prices | live prices panel shows on dashboard | Live Prices heading visible |
| 3 | Navigation | sidebar links navigate to correct pages | All 12 sidebar links |
| 4 | Strategy CRUD | create and delete a strategy | Create → verify → delete → verify gone |
| 5 | Backtest | form renders with fields and run button | Form fields visible |
| 6 | Backtest | clicking run triggers backtest submission | Page stays functional after click |
| 7 | Backtest | results display after mocked backtest run | Mocked results in `<pre>` block |
| 8 | Scheduler | create and delete a job | Job CRUD in table |
| 9 | Scheduler | toggle job enabled/disabled | Enabled ↔ Disabled toggle |
| 10 | Settings & Safety | page loads with safety controls | Safety controls heading visible |
| 11 | Settings & Safety | kill switch button is visible | Kill switch button present |
| 12 | Settings & Safety | kill switch toggles between kill and resume | KILL SWITCH → Resume → KILL SWITCH |
| 13 | Settings & Safety | add and delete a setting | Setting CRUD in table |
| 14 | Settings & Safety | safety number inputs are visible | Number inputs present |
| 15 | Data Explorer | page loads with form elements | Symbol input, date, Load button |
| 16 | Data Explorer | load button triggers data fetch | Page stable after Load click |
| 17 | Data Explorer | chart renders with mocked OHLCV data | Canvas element from mocked data |
| 18 | Optimize | page loads with form elements | Strategy selector, Run button, param grid |
| 19 | Optimize | strategy type selector changes param grid | Grid params update per strategy type |
| 20 | Optimize | advanced settings toggle | Show/hide walk-forward splits and train ratio |
| 21 | Optimize | results table displays with mocked optimization data | Ranked results with Sharpe, action buttons |
| 22 | Optimize | auto mode hides param grid and shows note | Auto mode UI behavior |
| 23 | Optimize | sweep results show comparison table | Strategy comparison with recommendations |
| 24 | Optimize | optimization history displays with mocked jobs | Job list with status and best Sharpe |
| 25 | Trades | page loads with trade history section | Trade History heading, table/empty state |
| 26 | Trades | asset type selector shows conditional fields | OPT shows expiry/strike/right, STK hides them |
| 27 | Trades | order confirmation modal shows and cancels | Review Order opens modal, Cancel closes it |
| 28 | Trades | populated table and P&L with mocked data | Mocked trades in table + P&L Summary |
| 29 | AI Chat | page loads with input and send button | Input + Send button visible |
| 30 | AI Chat | typing a message shows user bubble | User message as blue bubble |
| 31 | Agent | page loads with run button | Run Agent Now button + empty state |
| 32 | Agent | run button shows running state | Button text → "Running..." |
| 33 | Agent | logs display with mocked agent data | Mocked log card with analysis text |
| 34 | Risk | page loads with position sizing form | Position Sizing + Portfolio Risk headings |
| 35 | Risk | method dropdown changes param fields | percent_risk → kelly field switch |
| 36 | Risk | mocked position size result displays | Position size result from mocked API |
| 37 | Risk | mocked portfolio risk result displays | VaR, Sharpe from mocked API |
| 38 | Portfolio | page loads with optimization form | Portfolio Optimization heading + form |
| 39 | Portfolio | mocked optimization weights display | Weight table from mocked API |
| 40 | Portfolio | mocked tearsheet displays metrics | Tearsheet metrics from mocked API |
| 41 | Portfolio | mocked factor results display | Factor values from mocked API |
| 42 | Dashboard Account | account panel shows broker data | Cash, portfolio value from mocked API |
| 43 | Dashboard Account | account panel handles broker error | "Broker not connected" on API error |
| 44 | Optimize Live Adaptation | live adaptation section renders | Adaptation table from mocked API |
| 45 | Backtest Progress | progress indicator shows during backtest | Progress bar after mocked submit |

## Roadmap

### Production Readiness
- **Real broker integration testing** — Test Alpaca/IBKR price streaming and order flow with paper trading credentials
- **Tauri desktop build** — Wire the `desktop/` shell with the latest frontend + FastAPI sidecar
- **Authentication** — Add login flow for deployment beyond localhost (currently single-user with default user_id)

### Feature Depth
- **AI agent tool-use expansion** — Give the agent more Puffin tools (run backtests, adjust strategies, analyze risk)
- **Real-time backtest streaming** — Wire `/ws/backtest/{id}` to stream progress from long-running backtests (currently returns synchronously)
- **Desktop notifications** — Push alert notifications via Tauri native APIs

### Polish
- **Toast notifications** — Replace silent error swallowing with user-visible toast messages across all pages
- **Configurable dashboard** — Draggable/resizable panel grid for the 8-panel dashboard
- **Mobile responsive** — Test and tune grid layouts for small screens
