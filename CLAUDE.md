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

### Backend unit tests
```bash
pytest backend/tests/ -v
```

### Frontend E2E tests (Playwright)
Requires backend + frontend running (via Docker or standalone):
```bash
docker compose up -d backend frontend     # Ensure services are up
cd frontend
npx playwright install --with-deps        # First time only
npx playwright test --reporter=list       # Run all 18 E2E tests
```

E2E tests cover all 9 pages: Dashboard, Strategies, Backtest, Scheduler, Settings, Data Explorer, Trades, AI Chat, Agent.

## GitHub Pages / docs/ Setup
- Reference: ~/projects/puffin/docs/ for Jekyll tutorial site (separate concern)
- Puffling does not host its own docs site — documentation lives in the README and OpenSpec artifacts
