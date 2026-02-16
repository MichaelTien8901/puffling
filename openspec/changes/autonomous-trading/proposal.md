## Why

Puffling currently operates as a request-response application — users must manually trigger backtests, fetch data, and place orders. There is no way to monitor markets continuously, execute strategies live, or maintain a portfolio toward target allocations automatically. For a personal trading app to be truly useful, it needs to work autonomously between user sessions: watching markets, detecting signals, rebalancing portfolios, and alerting the user — all powered by the AI agent using the user's own LLM API key.

## What Changes

- **Background task scheduler** for periodic market scans, signal generation, and portfolio drift checks
- **Live strategy runner** that continuously generates signals from configured strategies and optionally executes trades
- **Goal-based portfolio manager** with target allocations, drift thresholds, and automated rebalancing
- **Alert system** for price targets, signal triggers, risk threshold breaches, and rebalance events
- **AI autonomous agent loop** that uses the user's Claude/OpenAI key to analyze market conditions, interpret signals, and recommend or execute actions
- **Safety controls** including kill switch, max daily trades, position limits, and mandatory confirmation for large orders
- **Paper trading mode enforcement** as default for all autonomous actions

## Capabilities

### New Capabilities
- `task-scheduler`: Background job scheduler for periodic execution of market scans, signal checks, rebalancing, and AI analysis tasks
- `live-strategy-runner`: Continuous strategy execution engine that generates signals from configured strategies and optionally places trades via the broker
- `portfolio-manager`: Goal-based portfolio management with target allocations, drift detection, and automated rebalancing using Puffin's RebalanceEngine
- `alert-system`: Configurable alerts for price targets, trading signals, risk thresholds, and portfolio events with UI notifications
- `autonomous-agent`: AI agent loop that periodically analyzes markets, interprets signals, and takes actions using the user's LLM API key and Puffin's tool-use capabilities

### Modified Capabilities
- `api-backend`: New REST/WebSocket endpoints for scheduler management, live strategy control, portfolio goals, and alerts
- `trading-dashboard`: New UI panels for monitoring active strategies, portfolio goals, alerts, and autonomous agent status

## Impact

- **New dependencies**: APScheduler or asyncio-based scheduler for background tasks
- **Backend changes**: New services for scheduler, live runner, portfolio manager, alerts, autonomous agent; new API routes and WebSocket channels
- **Frontend changes**: New dashboard widgets for active strategies, portfolio goals/drift, alert management, agent activity log
- **Database changes**: New tables for scheduled jobs, portfolio goals, alert configs, agent activity logs
- **Safety critical**: Autonomous trading requires robust safety controls — kill switch, position limits, paper trading default, confirmation for large orders
- **LLM API usage**: Autonomous agent will consume API credits on schedule — needs configurable frequency and budget controls
