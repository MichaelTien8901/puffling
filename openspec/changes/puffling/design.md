## Context

Puffin is a mature Python library with 17 modules covering data ingestion, alpha factors, portfolio optimization, ML/deep learning, NLP, RL, backtesting, broker integration, risk management, and AI-assisted trading. These modules expose well-defined classes (e.g., `DataProvider`, `Strategy`, `Backtester`, `LLMProvider`, `Broker`) following the Strategy pattern with pluggable implementations.

Currently, users interact via scripts or Jupyter notebooks. Puffling wraps this into a personal desktop application using FastAPI (backend API), Next.js (web UI), and Tauri (desktop shell). The architecture starts single-user but reserves multi-user isolation for future server deployment.

## Goals / Non-Goals

**Goals:**
- Expose all Puffin modules through a REST/WebSocket API without duplicating business logic
- Provide a rich, real-time trading dashboard (charts, portfolio, backtesting, AI chat)
- Ship as a single Tauri desktop executable for personal use on Linux/Windows
- Use SQLite for zero-config local storage with user-scoped schema
- Enable AI-powered natural language interaction with all trading capabilities
- Reserve multi-user extensibility via user_id scoping without implementing auth yet

**Non-Goals:**
- Multi-user authentication and authorization (future work)
- Mobile app or iOS/Android support
- Cloud deployment or horizontal scaling (future work)
- Replacing Jupyter notebooks for research/exploration workflows
- Building a new charting library (use TradingView lightweight-charts)
- Real-time sub-millisecond HFT execution

## Decisions

### 1. Project structure: Puffling as a separate repository

**Decision:** Puffling lives in its own repo at `~/projects/puffling/`, separate from Puffin (`~/projects/puffin/`). Puffin is consumed as a pip dependency.

**Rationale:** Puffling is an application; Puffin is a library. Separate repos give independent release cycles, cleaner CI/CD, simpler Tauri builds (Tauri expects to own the repo root), and smaller clones (no PDFs/notebooks/docs). During development, install Puffin as an editable dependency (`pip install -e ~/projects/puffin`); in production, install from PyPI or a pinned git ref.

**Alternatives considered:**
- Subdirectory of Puffin repo → conflates library with application, complicates Tauri builds
- Monorepo with workspaces → unnecessary complexity for a personal tool

```
~/projects/puffling/         # Separate repo
├── backend/                 # FastAPI
│   ├── api/
│   │   ├── routes/          # REST endpoints grouped by domain
│   │   └── ws/              # WebSocket handlers
│   ├── services/            # Thin wrappers around puffin modules
│   ├── models/              # SQLAlchemy ORM models
│   ├── core/                # Config, database, dependencies
│   └── main.py
├── frontend/                # Next.js app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/             # API client, WebSocket helpers
│   └── package.json
├── desktop/                 # Tauri shell
│   ├── src-tauri/
│   └── tauri.conf.json
├── pyproject.toml           # Depends on puffin
├── docker-compose.yml
└── README.md
```

### 2. Backend API design: Domain-grouped REST + WebSocket

**Decision:** Organize API routes by Puffin domain modules. Use REST for CRUD/request-response and WebSocket for real-time streaming.

**Rationale:** Maps directly to Puffin's module structure, making the API intuitive. WebSocket is essential for live price feeds and backtest progress.

**REST routes:**
| Route group | Puffin module | Key endpoints |
|---|---|---|
| `/api/data` | `puffin.data` | GET symbols, OHLCV, fundamentals |
| `/api/factors` | `puffin.factors` | POST compute factors, GET factor library |
| `/api/strategies` | `puffin.strategies` | CRUD strategy configs, POST generate signals |
| `/api/backtest` | `puffin.backtest` | POST run backtest, GET results |
| `/api/portfolio` | `puffin.portfolio` | POST optimize, GET tearsheet |
| `/api/models` | `puffin.models`, `puffin.ensembles`, `puffin.ml` | POST train, POST predict |
| `/api/ai` | `puffin.ai` | POST chat, POST sentiment, GET report |
| `/api/broker` | `puffin.broker` | GET positions, POST order, GET account |
| `/api/risk` | `puffin.risk` | GET portfolio risk, POST position size |
| `/api/monitor` | `puffin.monitor` | GET trade log, GET PnL, GET health |
| `/api/settings` | `user-data-store` | CRUD user preferences |

**WebSocket channels:**
| Channel | Purpose |
|---|---|
| `/ws/prices` | Real-time price streaming |
| `/ws/backtest/{id}` | Backtest progress & live results |
| `/ws/trades` | Live trade notifications |
| `/ws/ai/chat` | Streaming AI responses |

### 3. Service layer: Thin wrappers, not rewrites

**Decision:** Backend services are thin adapters that instantiate and call Puffin classes. No business logic duplication.

**Rationale:** Puffin modules already implement the trading logic. Services handle request parsing, async coordination, and database persistence.

```python
# Example: backtest service
class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    async def run(self, config: BacktestRequest, user_id: str) -> BacktestResult:
        strategy = get_strategy(config.strategy_name, config.params)
        provider = YFinanceProvider()
        backtester = Backtester(strategy, provider)
        result = backtester.run(config.symbols, config.start, config.end)
        # Persist result
        self.db.add(BacktestRecord(user_id=user_id, result=result.to_dict()))
        self.db.commit()
        return result
```

### 4. Database: SQLite with user-scoped schema

**Decision:** SQLite via SQLAlchemy with all tables carrying a `user_id` column. Single-user mode auto-provisions a default user (`default`).

**Rationale:** Zero config for personal use. SQLite is file-based, embeds in Tauri easily. The `user_id` column costs nothing now but enables multi-user isolation later by adding auth middleware.

**Key tables:**
- `users` — id, name, created_at (single row in personal mode)
- `settings` — user_id, key, value (JSON)
- `strategy_configs` — user_id, name, strategy_type, params (JSON)
- `backtest_results` — user_id, strategy_id, metrics (JSON), created_at
- `trade_history` — user_id, symbol, side, qty, price, timestamp
- `watchlists` — user_id, name, symbols (JSON)
- `ai_conversations` — user_id, messages (JSON), created_at

### 5. Frontend: Next.js with App Router

**Decision:** Next.js 14+ with App Router, TypeScript, Tailwind CSS, and TradingView lightweight-charts.

**Rationale:** App Router provides layouts, loading states, and server components. TradingView lightweight-charts is the standard for financial charting. Tailwind enables rapid UI development.

**Page structure:**
- `/` — Dashboard (portfolio summary, watchlist, recent trades)
- `/backtest` — Strategy selection, parameter config, results with charts
- `/strategies` — Strategy management, signal viewer
- `/ai` — Chat interface with the trading AI agent
- `/data` — Data explorer, factor analysis
- `/trades` — Trade history, PnL attribution
- `/settings` — App configuration, API keys, preferences

### 6. Desktop: Tauri with FastAPI sidecar

**Decision:** Tauri v2 bundles the Next.js static export as the WebView content and spawns FastAPI as a sidecar subprocess.

**Rationale:** Tauri uses the OS WebView (~5MB overhead vs Electron's ~150MB). The sidecar pattern keeps Python and Rust decoupled — Tauri manages the window, FastAPI handles all logic.

**Startup flow:**
1. Tauri launches → spawns `uvicorn puffling.backend.main:app` as sidecar
2. Waits for FastAPI health check (`/api/health`) to respond
3. Loads Next.js static export in WebView pointing at `localhost:<port>`
4. On close → sends SIGTERM to sidecar, waits for graceful shutdown

**Bundling:** Use PyInstaller or `uv` to create a self-contained Python bundle for the sidecar, included in the Tauri app bundle.

### 7. AI agent: Conversational interface over Puffin's ai module

**Decision:** The AI chat uses Puffin's `LLMProvider` (Claude/OpenAI) with tool-use to invoke any Puffin capability via the backend API.

**Rationale:** Tool-use/function-calling lets the LLM decide which Puffin module to invoke based on natural language. The backend defines tools that map to API endpoints.

**Available tools for the AI agent:**
- `get_market_data` → `/api/data`
- `run_backtest` → `/api/backtest`
- `analyze_sentiment` → `/api/ai/sentiment`
- `compute_factors` → `/api/factors`
- `optimize_portfolio` → `/api/portfolio`
- `place_order` → `/api/broker` (with confirmation)
- `check_risk` → `/api/risk`

## Risks / Trade-offs

- **Tauri sidecar complexity** → Bundling Python with Tauri adds build complexity. Mitigation: use `uv` for reproducible Python environments; provide Docker fallback for users who skip Tauri.
- **SQLite concurrency** → SQLite has limited write concurrency. Mitigation: acceptable for single-user; multi-user future would migrate to PostgreSQL (SQLAlchemy makes this a config change).
- **Next.js static export limitations** → Static export can't use server-side features (API routes, SSR). Mitigation: all data comes from FastAPI; Next.js is purely client-side rendering.
- **FastAPI sidecar startup time** → Python + ML imports can be slow. Mitigation: lazy-import heavy modules (PyTorch, etc.) only when first used; show loading state in Tauri.
- **AI tool-use safety** → LLM could invoke destructive actions (e.g., place real trades). Mitigation: all broker actions require explicit user confirmation in the UI; paper trading mode by default.

## Open Questions

- **Python bundling for Tauri**: PyInstaller vs `uv` standalone vs embedded Python — needs prototyping to determine bundle size and startup time
- **Backtest compute**: Should long-running backtests use background tasks (Celery/ARQ) or is async FastAPI sufficient for single-user?
- **Chart library**: TradingView lightweight-charts vs Recharts — TradingView is more feature-rich but has licensing considerations
