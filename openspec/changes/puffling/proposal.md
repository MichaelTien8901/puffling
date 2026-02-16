## Why

The Puffin project has a growing library of algorithmic trading modules (data, strategies, ML, AI, backtesting, risk) but no unified application to use them. Users must write scripts or Jupyter notebooks to interact with the system. Puffling is an AI-powered trading application that wraps Puffin's capabilities into a personal desktop app with a rich web UI, making algorithmic trading accessible without writing code. Starting as a single-user personal tool (via Tauri desktop), the architecture reserves multi-user extensibility for future server deployment.

## What Changes

- **New FastAPI backend** (`puffling/backend/`) that exposes Puffin's Python modules as REST and WebSocket APIs
- **New Next.js frontend** (`puffling/frontend/`) providing a rich trading dashboard with real-time charts, backtesting UI, AI chat, and portfolio views
- **Tauri desktop wrapper** (`puffling/desktop/`) for personal use — bundles the frontend WebView with FastAPI as a sidecar process, single executable for Linux/Windows
- **SQLite database** for personal storage — user settings, trading history, strategy configs, cached data
- **AI agent integration** — LLM-powered trading assistant using Puffin's existing `ai/` module for market analysis, signal interpretation, and strategy suggestions
- **Multi-user architecture reserved** — database schema uses user_id foreign keys, API routes accept user context, settings are user-scoped; single-user mode auto-provisions a default user

## Capabilities

### New Capabilities
- `api-backend`: FastAPI application exposing Puffin modules as REST/WebSocket endpoints (data, strategies, backtesting, ML, AI, broker)
- `trading-dashboard`: Next.js frontend with real-time charts, portfolio view, trade history, strategy management, and AI chat panel
- `desktop-app`: Tauri wrapper bundling frontend + FastAPI sidecar for personal single-executable deployment on Linux/Windows
- `user-data-store`: SQLite-based storage for user settings, strategy configs, trading history, and cached market data with user-scoped schema
- `ai-trading-agent`: LLM-powered assistant for market analysis, signal interpretation, strategy suggestions, and natural language trading commands

### Modified Capabilities
<!-- No existing specs to modify -->

## Impact

- **New directories**: `puffling/backend/`, `puffling/frontend/`, `puffling/desktop/`
- **Dependencies added**: FastAPI, uvicorn, SQLAlchemy, Next.js, React, Tauri, TradingView lightweight-charts
- **Puffin modules consumed**: `puffin.data`, `puffin.strategies`, `puffin.backtest`, `puffin.ml`, `puffin.ai`, `puffin.broker`, `puffin.risk`, `puffin.monitor`
- **Docker**: `docker-compose.yml` for backend + frontend (server mode), separate Tauri build for desktop
- **Build tooling**: Rust toolchain required for Tauri desktop builds; Node.js for frontend; Python 3.11+ for backend
