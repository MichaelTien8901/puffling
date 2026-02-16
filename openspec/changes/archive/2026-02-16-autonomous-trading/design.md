## Context

Puffling is a personal AI-powered trading app wrapping Puffin's library. The base `puffling` change provides a request-response UI and API. This change adds autonomous capabilities: background scheduling, live strategy execution, goal-based portfolio management, alerts, and an AI agent loop — all running unattended between user sessions.

Puffin already provides: `RebalanceEngine`, `rebalance_schedule()`, `StopLossManager`, `PortfolioRiskManager`, strategy `generate_signals()`, `AlpacaBroker` with safety validators, and `LLMProvider` with tool-use. This change orchestrates these into autonomous workflows.

## Goals / Non-Goals

**Goals:**
- Run configured strategies on a schedule, generating signals and optionally executing trades
- Maintain portfolios toward user-defined target allocations with drift-based rebalancing
- Alert users on price targets, signal triggers, risk breaches, and rebalance events
- Provide an AI agent that periodically analyzes markets and takes actions using the user's LLM key
- Enforce safety at every level: paper trading default, position limits, daily trade caps, kill switch

**Non-Goals:**
- Sub-second HFT execution (scheduling granularity is minutes, not microseconds)
- Multi-user concurrent scheduling (single-user personal app)
- Custom alert delivery channels (email, SMS) — UI notifications only for now
- Replacing the user's judgment — autonomous actions are bounded and confirmable

## Decisions

### 1. Scheduler: asyncio background tasks with APScheduler

**Decision:** Use APScheduler with asyncio backend, persisting job configs to SQLite. Jobs run in the FastAPI process.

**Rationale:** Single-user app doesn't need Celery/Redis overhead. APScheduler integrates cleanly with asyncio and supports cron-like schedules. Job configs persisted to DB survive restarts.

**Job types:**
- `market_scan` — periodic signal generation from configured strategies
- `portfolio_check` — drift detection and optional rebalancing
- `ai_analysis` — AI agent market review
- `alert_check` — price/risk threshold monitoring

### 2. Live strategy runner: event loop with configurable actions

**Decision:** Each configured strategy can be set to one of three modes: `monitor` (signals only), `alert` (signals + notifications), `auto-trade` (signals + execution with safety checks).

**Rationale:** Graduated autonomy lets users start with monitoring and gain confidence before enabling auto-trading.

### 3. Portfolio manager: target weights with drift threshold

**Decision:** Users define target allocations (e.g., SPY 60%, AGG 30%, GLD 10%) with a drift threshold (e.g., 5%). When any position drifts beyond threshold, the system calculates rebalance trades using Puffin's `RebalanceEngine` and either alerts or executes.

**Rationale:** Simple, proven approach. Puffin's `RebalanceEngine` already handles trade generation with cost modeling.

### 4. Safety controls: layered defense

**Decision:** Multiple safety layers, all enabled by default:
- Paper trading mode (default, must explicitly enable live)
- Kill switch (instantly halts all autonomous trading)
- Max daily trades limit (default: 10)
- Max position size limit (default: 10% of portfolio)
- Large order confirmation (orders > configurable threshold require manual approval)
- Puffin's `SafetyController` validators (position sizing, trading hours, symbol whitelist)

### 5. Autonomous AI agent: scheduled analysis with bounded actions

**Decision:** The AI agent runs on a configurable schedule (e.g., daily morning), uses the user's Claude/OpenAI key, reviews market conditions, portfolio status, and active signals, then produces a report and optionally suggests/executes actions.

**Rationale:** Tool-use lets the LLM invoke the same capabilities as the chat interface, but autonomously. Budget controls (max API calls per run, max daily spend) prevent runaway costs.

**Agent loop:**
1. Gather context: portfolio positions, active signals, recent alerts, market data
2. Analyze via LLM with tool-use
3. Produce report (always)
4. Suggest actions (if configured)
5. Execute actions (only if auto-trade enabled + safety checks pass)

### 6. New database tables

- `scheduled_jobs` — job_id, user_id, job_type, schedule (cron), config (JSON), enabled
- `portfolio_goals` — id, user_id, name, target_weights (JSON), drift_threshold, rebalance_mode
- `alert_configs` — id, user_id, alert_type, condition (JSON), enabled
- `alert_history` — id, user_id, alert_config_id, triggered_at, message
- `agent_logs` — id, user_id, run_at, report (JSON), actions_taken (JSON)

### 7. New API endpoints

**REST:**
- `/api/scheduler` — CRUD scheduled jobs, start/stop, get status
- `/api/portfolio/goals` — CRUD portfolio goals, get drift status
- `/api/alerts` — CRUD alert configs, get alert history
- `/api/agent` — get agent logs, configure agent schedule, trigger manual run
- `/api/safety` — get/set safety controls, kill switch

**WebSocket:**
- `/ws/alerts` — real-time alert notifications
- `/ws/agent` — live agent activity stream

## Risks / Trade-offs

- **Unattended trading risk** → Mitigated by layered safety controls and paper trading default
- **LLM API cost** → Mitigated by configurable frequency and budget caps
- **Scheduler reliability** → In-process scheduler dies with the app; acceptable for personal desktop use
- **Strategy drift** → Market conditions change; users must review and adjust periodically

## Open Questions

- Should the agent have a "confidence threshold" below which it only reports but doesn't act?
- Should rebalancing support tax-loss harvesting awareness?
