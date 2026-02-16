# Puffling - AI-Powered Algorithmic Trading App

## Project Overview
Puffling is a personal AI-powered trading application built on [Puffin](https://github.com/MichaelTien8901/puffin). It wraps Puffin's algorithmic trading library into a desktop app with a rich web UI.

## Architecture
- **Backend**: FastAPI (Python 3.11+) — REST/WebSocket API wrapping Puffin modules
- **Frontend**: Next.js 14+ (TypeScript, Tailwind CSS) — Trading dashboard with TradingView charts
- **Desktop**: Tauri v2 — Native shell bundling frontend + FastAPI sidecar
- **Database**: SQLite via SQLAlchemy — User-scoped schema for future multi-user

## Project Structure
```
puffling/
├── backend/             # FastAPI application
│   ├── api/
│   │   ├── routes/      # REST endpoints by domain
│   │   └── ws/          # WebSocket handlers
│   ├── services/        # Thin wrappers around Puffin modules
│   ├── models/          # SQLAlchemy ORM models
│   ├── core/            # Config, database, dependencies
│   └── main.py
├── frontend/            # Next.js app
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── lib/         # API client, WebSocket helpers
├── desktop/             # Tauri shell
│   └── src-tauri/
├── openspec/            # Change management
└── pyproject.toml
```

## Dependencies
- **Puffin library**: `pip install -e ~/projects/puffin` (editable install during development)
- Backend: FastAPI, uvicorn, SQLAlchemy, pydantic
- Frontend: Next.js, React, TradingView lightweight-charts, Tailwind CSS
- Desktop: Tauri v2 (requires Rust toolchain)

## Conventions
- Backend services are thin adapters — business logic stays in Puffin, not duplicated here
- All database tables carry `user_id` for future multi-user (default user auto-provisioned)
- REST routes grouped by Puffin domain: `/api/data`, `/api/strategies`, `/api/backtest`, etc.
- WebSocket for real-time: `/ws/prices`, `/ws/backtest/{id}`, `/ws/trades`, `/ws/ai/chat`
- AI agent uses LLM tool-use to invoke Puffin capabilities via backend API
- Broker actions always require explicit user confirmation

## Building & Running

### Docker (recommended)
```bash
docker compose up -d backend frontend    # Start backend + frontend
docker compose down                       # Stop all services
```

### Backend (standalone)
```bash
pip install -e .                          # Install puffling + dependencies
pip install -e ~/projects/puffin          # Install puffin (editable)
uvicorn backend.main:app --reload         # Run on http://localhost:8000
```

### Frontend (standalone)
```bash
cd frontend
npm install
npm run dev                               # Dev server on http://localhost:3000
npm run build                             # Production build
```

## Testing

### Backend unit tests (Docker — recommended)
Uses the `test-backend` service which auto-installs Puffin and runs pytest:
```bash
docker compose run --rm test-backend      # Runs all 30 backend tests
```

To run a specific test file:
```bash
docker compose run --rm test-backend sh -c \
  "uv pip install --system --no-build-isolation /puffin && pytest tests/test_optimizer.py -v"
```

### Backend unit tests (standalone)
Requires Puffin installed locally (`pip install -e ~/projects/puffin`):
```bash
pip install -e ".[dev]"                   # Install puffling + dev deps (pytest, httpx, ruff)
pytest tests/ -v                          # Run all 30 backend tests
```

### Frontend E2E tests (Playwright)
Requires backend + frontend running (via Docker or standalone):
```bash
docker compose up -d backend frontend     # Ensure services are up
cd frontend
npx playwright install --with-deps        # First time only
npx playwright test --reporter=list       # Run all 28 E2E tests
```

To run a specific test by name:
```bash
cd frontend
npx playwright test --reporter=list -g "chart renders"
```

E2E tests cover all 10 pages: Dashboard, Strategies, Backtest, Optimize, Scheduler, Settings, Data Explorer, Trades, AI Chat, Agent. Tests use `page.route()` mocks for trade data, P&L, OHLCV charts, backtest results, and agent logs.

### Test inventory

#### Backend tests (30) — `docker compose run --rm test-backend`

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
| 11 | test_e2e.py | test_app_starts_and_health | App startup and health check |
| 12 | test_e2e.py | test_full_strategy_flow | Strategy create → backtest flow |
| 13 | test_e2e.py | test_settings_roundtrip | Settings set → get → delete |
| 14 | test_e2e.py | test_model_types_available | ML model types available |
| 15 | test_e2e.py | test_factor_library_available | Factor library accessible |
| 16 | test_optimizer.py | test_default_grids_exist | Default param grids for all 4 strategies |
| 17 | test_optimizer.py | test_grid_size_validation | Rejects grids > 500 combinations |
| 18 | test_optimizer.py | test_data_length_validation | Rejects insufficient data length |
| 19 | test_optimizer.py | test_expand_grid | Grid expansion to parameter combos |
| 20 | test_optimizer.py | test_default_grid_sizes_within_limit | All default grids under limit |
| 21 | test_optimizer.py | test_list_jobs_empty | Empty job list returns [] |
| 22 | test_optimizer.py | test_get_job_not_found | 404 for missing job |
| 23 | test_optimizer.py | test_submit_strategy_optimization | Submit optimization returns job_id |
| 24 | test_optimizer.py | test_submit_with_oversized_grid | 400 for oversized grid |
| 25 | test_optimizer.py | test_cancel_nonexistent_job | 404 for cancelling missing job |
| 26 | test_optimizer.py | test_list_jobs_after_submit | Job appears in list after submit |
| 27 | test_services.py | test_settings_service | SettingsService CRUD operations |
| 28 | test_services.py | test_model_service_list_types | ModelService type listing |
| 29 | test_strategy_runner.py | test_activate_deactivate | Strategy activation toggle |
| 30 | test_strategy_runner.py | test_auto_trade_blocked_by_kill_switch | Kill switch blocks auto-trade |

#### Frontend E2E tests (28) — `cd frontend && npx playwright test --reporter=list`

Requires: `docker compose up -d backend frontend`

| # | Suite | Test | Description |
|---|-------|------|-------------|
| 1 | Dashboard | loads and shows panels | Page heading + 4 panel headings |
| 2 | Navigation | sidebar links navigate to correct pages | All 10 sidebar links |
| 3 | Strategy CRUD | create and delete a strategy | Create → verify → delete → verify gone |
| 4 | Backtest | form renders with fields and run button | Form fields visible |
| 5 | Backtest | clicking run triggers backtest submission | Page stays functional after click |
| 6 | Backtest | results display after mocked backtest run | Mocked results in `<pre>` block |
| 7 | Scheduler | create and delete a job | Job CRUD in table |
| 8 | Scheduler | toggle job enabled/disabled | Enabled ↔ Disabled toggle |
| 9 | Settings & Safety | page loads with safety controls | Safety controls heading visible |
| 10 | Settings & Safety | kill switch button is visible | Kill switch button present |
| 11 | Settings & Safety | kill switch toggles between kill and resume | KILL SWITCH → Resume → KILL SWITCH |
| 12 | Settings & Safety | add and delete a setting | Setting CRUD in table |
| 13 | Settings & Safety | safety number inputs are visible | Number inputs present |
| 14 | Data Explorer | page loads with form elements | Symbol input, date, Load button |
| 15 | Data Explorer | load button triggers data fetch | Page stable after Load click |
| 16 | Data Explorer | chart renders with mocked OHLCV data | Canvas element from mocked data |
| 17 | Optimize | page loads with form elements | Strategy selector, Run button, param grid |
| 18 | Optimize | strategy type selector changes param grid | Grid params update per strategy type |
| 19 | Optimize | advanced settings toggle | Show/hide walk-forward splits and train ratio |
| 20 | Optimize | results table displays with mocked optimization data | Ranked results with Sharpe, action buttons |
| 21 | Optimize | optimization history displays with mocked jobs | Job list with status and best Sharpe |
| 22 | Trades | page loads with trade history section | Trade History heading, table/empty state |
| 23 | Trades | populated table and P&L with mocked data | Mocked trades in table + P&L Summary |
| 24 | AI Chat | page loads with input and send button | Input + Send button visible |
| 25 | AI Chat | typing a message shows user bubble | User message as blue bubble |
| 26 | Agent | page loads with run button | Run Agent Now button + empty state |
| 27 | Agent | run button shows running state | Button text → "Running..." |
| 28 | Agent | logs display with mocked agent data | Mocked log card with analysis text |

## GitHub Pages / docs/ Setup
- Reference: ~/projects/puffin/docs/ for Jekyll tutorial site (separate concern)
- Puffling does not host its own docs site — documentation lives in the README and OpenSpec artifacts
