## 1. Project Setup

- [ ] 1.1 Initialize backend Python package with pyproject.toml dependencies (FastAPI, uvicorn, SQLAlchemy, pydantic)
- [ ] 1.2 Initialize frontend Next.js 14+ app with TypeScript, Tailwind CSS, TradingView lightweight-charts
- [ ] 1.3 Initialize Tauri v2 desktop project with sidecar configuration
- [ ] 1.4 Set up docker-compose.yml for backend + frontend dev mode

## 2. Database & Models

- [ ] 2.1 Create SQLAlchemy database engine and session setup in backend/core/database.py
- [ ] 2.2 Create User model and auto-provision default user on startup
- [ ] 2.3 Create Settings model (user_id, key, value JSON)
- [ ] 2.4 Create StrategyConfig model (user_id, name, strategy_type, params JSON)
- [ ] 2.5 Create BacktestResult model (user_id, strategy_id, metrics JSON, created_at)
- [ ] 2.6 Create TradeHistory model (user_id, symbol, side, qty, price, timestamp)
- [ ] 2.7 Create Watchlist model (user_id, name, symbols JSON)
- [ ] 2.8 Create AIConversation model (user_id, messages JSON, created_at)

## 3. Backend Services

- [ ] 3.1 Create DataService wrapping Puffin DataProvider (OHLCV, symbols, fundamentals)
- [ ] 3.2 Create StrategyService wrapping Puffin strategies (CRUD configs, generate signals)
- [ ] 3.3 Create BacktestService wrapping Puffin Backtester (run, persist results)
- [ ] 3.4 Create PortfolioService wrapping Puffin portfolio (optimize, tearsheet)
- [ ] 3.5 Create ModelService wrapping Puffin ml, deep, ensembles, and rl modules (train, predict, list model types)
- [ ] 3.6 Create AIService wrapping Puffin LLMProvider and nlp module (chat, sentiment with Loughran-McDonald lexicon, topic modeling, reports)
- [ ] 3.7 Create BrokerService wrapping Puffin Broker (positions, orders with confirmation flow)
- [ ] 3.8 Create RiskService wrapping Puffin risk module (portfolio risk, position sizing)
- [ ] 3.9 Create MonitorService wrapping Puffin monitor (trade log, PnL, health)
- [ ] 3.10 Create SettingsService for user preferences CRUD

## 4. REST API Routes

- [ ] 4.1 Create FastAPI app entry point with health check endpoint at /api/health
- [ ] 4.2 Create /api/data routes (GET symbols, OHLCV, fundamentals)
- [ ] 4.3 Create /api/factors routes (POST compute, GET factor library, POST risk-factors via PCA, POST cluster assets)
- [ ] 4.4 Create /api/strategies routes (CRUD configs, POST generate signals)
- [ ] 4.5 Create /api/backtest routes (POST run, GET results)
- [ ] 4.6 Create /api/portfolio routes (POST optimize, GET tearsheet)
- [ ] 4.7 Create /api/models routes (POST train, POST predict, GET types — supporting ml, deep, ensembles, rl backends)
- [ ] 4.8 Create /api/ai routes (POST chat, POST sentiment with NLP lexicons, POST topics, GET report)
- [ ] 4.9 Create /api/broker routes (GET positions, POST order with confirmation, GET account)
- [ ] 4.10 Create /api/risk routes (GET portfolio risk, POST position size)
- [ ] 4.11 Create /api/monitor routes (GET trade log, GET PnL, GET health)
- [ ] 4.12 Create /api/settings routes (CRUD user preferences)
- [ ] 4.13 Add default user dependency injection for all routes

## 5. WebSocket Handlers

- [ ] 5.1 Create /ws/prices handler for real-time price streaming
- [ ] 5.2 Create /ws/backtest/{id} handler for backtest progress streaming
- [ ] 5.3 Create /ws/trades handler for live trade notifications
- [ ] 5.4 Create /ws/ai/chat handler for streaming AI responses

## 6. Frontend Core

- [ ] 6.1 Set up API client library for REST calls in frontend/src/lib/
- [ ] 6.2 Set up WebSocket helper hooks in frontend/src/hooks/
- [ ] 6.3 Create app layout with persistent navigation sidebar
- [ ] 6.4 Create TradingView chart component wrapper (candlestick, equity curve)

## 7. Frontend Pages

- [ ] 7.1 Create Dashboard page (/) with portfolio summary, watchlist, recent trades
- [ ] 7.2 Create Backtest page (/backtest) with strategy selection, params, results chart
- [ ] 7.3 Create Strategies page (/strategies) with CRUD and signal viewer
- [ ] 7.4 Create AI Chat page (/ai) with streaming message display and action results
- [ ] 7.5 Create Data Explorer page (/data) with symbol search and factor analysis
- [ ] 7.6 Create Trades page (/trades) with trade history and PnL attribution
- [ ] 7.7 Create Settings page (/settings) with API keys and preferences

## 8. AI Trading Agent

- [ ] 8.1 Define AI tool schemas for all 7 tools (get_market_data, run_backtest, analyze_sentiment, compute_factors, optimize_portfolio, place_order, check_risk)
- [ ] 8.2 Implement tool execution handlers mapping tools to backend API calls
- [ ] 8.3 Implement broker action confirmation flow in AI chat UI
- [ ] 8.4 Set paper trading as default mode with live trading toggle in settings
- [ ] 8.5 Implement AI conversation persistence and history retrieval

## 9. Desktop App

- [ ] 9.1 Configure Tauri sidecar to spawn FastAPI (uvicorn) on startup
- [ ] 9.2 Implement health check polling before loading WebView
- [ ] 9.3 Implement graceful shutdown (SIGTERM to sidecar on window close)
- [ ] 9.4 Configure Next.js static export for Tauri WebView embedding
- [ ] 9.5 Set up Python bundling (uv/PyInstaller) for self-contained sidecar
- [ ] 9.6 Configure Tauri build targets for Linux (AppImage) and Windows (.msi)

## 10. Integration & Testing

- [ ] 10.1 Add backend API tests for all route groups
- [ ] 10.2 Add service layer tests verifying Puffin module delegation
- [ ] 10.3 Add frontend component tests for chart and chat components
- [ ] 10.4 End-to-end smoke test: launch app, run backtest, view results
