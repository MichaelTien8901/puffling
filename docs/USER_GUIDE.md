# Puffling User Guide

Puffling is a personal AI-powered algorithmic trading application. This guide walks you through every page and feature.

## Getting Started

### 1. Configure Alpaca Broker

Puffling connects to [Alpaca](https://alpaca.markets) for trading. You need a free Alpaca account to submit orders and view positions.

1. Sign up at https://app.alpaca.markets/signup (free — just email and password)
2. Go to **Dashboard > API Keys** and generate a new key pair
3. Copy your API Key and Secret Key
4. Create a `.env` file in the project root (copy from the template):

```bash
cp .env.example .env
```

5. Edit `.env` with your credentials:

```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

**Paper trading** is enabled by default — you trade with virtual money (~$100k) so there's no financial risk. The same Alpaca credentials work for both paper and live trading; Puffling controls which mode via the Settings page.

> **Without Alpaca credentials:** The app still works for backtesting, optimization, data exploration, and strategy management. Only order submission and portfolio/position viewing require Alpaca.

#### Canadian Users & Non-US Residents

Alpaca's **live trading** (real money) requires US residency, but **paper trading works for everyone worldwide** — no identity verification or US address needed. You get paper trading API keys immediately after signing up.

For **live trading from Canada**, use Interactive Brokers (see below).

### 1b. Configure Interactive Brokers (IBKR)

Puffling supports [Interactive Brokers](https://www.interactivebrokers.ca) as an alternative broker. IBKR accepts Canadian residents and provides full API access for US-listed stocks.

**Setup:**

1. Sign up at https://www.interactivebrokers.ca (or .com for US)
2. Enable a **paper trading account** (free) from Account Management
3. Download and install **IB Gateway** (recommended) or **TWS**:
   - IB Gateway: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
   - Lighter weight, headless — preferred for algo trading
4. Launch IB Gateway, log in with your paper trading credentials
5. In your `.env` file, set:

```
BROKER=ibkr
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=1
```

**Port reference:**
| Application | Paper | Live |
|-------------|-------|------|
| IB Gateway  | 4002  | 4001 |
| TWS         | 7497  | 7496 |

**IB Gateway configuration:**
- In IB Gateway settings, go to **API > Settings**
- Check "Enable ActiveX and Socket Clients"
- Uncheck "Read-Only API" (required for order submission)
- Add `127.0.0.1` to trusted IPs

**Install the IBKR dependency** in Puffin:
```bash
pip install -e ~/projects/puffin[ibkr]
```

> **Note:** IB Gateway/TWS must be running whenever Puffling needs broker access. If the connection drops, Puffling will attempt to reconnect on the next request.

### 2. Start the App

1. Start the app: `docker compose up -d backend frontend`
2. Open http://localhost:3000 in your browser
3. The sidebar on the left provides navigation to all pages

## Pages

### Dashboard

The home page shows an overview of your trading activity:

- **Portfolio** — Current positions from your broker (symbol, quantity, average price, current price)
- **Active Strategies** — Strategies currently running in monitor, alert, or auto-trade mode
- **Portfolio Goals** — Target allocation goals and drift thresholds
- **Recent Trades** — Latest executed trades
- **Recent Alerts** — Real-time alert feed (updates live via WebSocket)

### Strategies

Create and manage trading strategy configurations.

**Creating a strategy:**
1. Enter a name (e.g., "my_momentum")
2. Enter a strategy type: `momentum`, `mean_reversion`, `stat_arb`, or `market_making`
3. Click **Create**

The strategy appears in the "Saved Strategies" table. Click **Delete** to remove it.

Strategies are configurations — they define which algorithm and parameters to use. They don't trade on their own until activated through the Scheduler or Agent.

### Backtest

Test a strategy against historical data to see how it would have performed.

1. Enter a strategy type (e.g., `momentum`)
2. Enter symbols (e.g., `SPY` or `SPY, QQQ` for multiple)
3. Pick a date range
4. Click **Run Backtest**

Results show performance metrics including total return, Sharpe ratio, max drawdown, and win rate.

### Optimize

Find the best parameters for a strategy using walk-forward analysis.

**Single strategy optimization:**
1. Select a strategy type from the dropdown
2. Enter symbols and date range
3. The parameter grid auto-fills with defaults — adjust values as needed (comma-separated)
4. Click **Run Optimization**
5. Results show ranked parameter combinations sorted by Sharpe ratio
6. Click **Backtest** to verify a result, or **Save as Strategy** to keep it

**Auto mode (all strategies):**
1. Select "Auto (all strategies)" from the dropdown
2. This runs optimization across all 4 strategy types using default grids
3. Results show a comparison table with the best result per strategy
4. A recommendation highlights the best overall strategy with a confidence level

**Advanced settings** (click "Show Advanced Settings"):
- **Walk-Forward Splits** — Number of train/test periods (default: 5)
- **Train Ratio** — Fraction of each split used for training (default: 0.7)

**Optimization History** at the bottom shows all past jobs. Click **View Results** to reload results from a previous run.

### Trades

View trade history and submit new orders.

**Submitting an order:**
1. Fill in the order form at the top:
   - **Symbol** — Ticker symbol (e.g., SPY, AAPL)
   - **Side** — BUY or SELL
   - **Quantity** — Number of shares
   - **Order Type** — market (default) or limit
2. Click **Submit Order**
3. The order is sent to your connected broker (Alpaca)

**Trade History** shows all executed trades with symbol, side, quantity, price, and timestamp.

**P&L Summary** shows aggregate profit/loss and win rate when trades exist.

> **Note:** Orders require a connected Alpaca broker account. Without broker credentials configured, order submission will return an error.

### Data Explorer

View historical OHLCV (Open, High, Low, Close, Volume) price data.

1. Enter a symbol (e.g., `AAPL`)
2. Pick a date range
3. Click **Load**

A candlestick chart renders showing the price history. Data is fetched from Yahoo Finance via Puffin.

### AI Chat

Chat with an AI assistant about trading strategies, market analysis, and portfolio decisions.

Type a message and press Enter or click Send. The AI responds using Claude or OpenAI (configured in backend settings).

### Agent

View the autonomous trading agent's activity logs. The agent periodically analyzes your portfolio and market conditions, then suggests or executes trades based on your safety settings.

- Click **Trigger Run** to manually run the agent
- View past run reports including analysis and actions taken

### Scheduler

Manage scheduled jobs that run automatically on a cron schedule.

- View active jobs, their schedules, and next run times
- Start/stop scheduled tasks

### Settings

Configure safety controls and application settings.

**Safety Controls:**
- **Kill Switch** — Immediately halts all autonomous trading. Click again to resume.
- **Paper Trading** — Toggle between paper (simulated) and live trading
- **Max Daily Trades** — Limit on trades per day
- **Max Position Size (%)** — Maximum portfolio allocation per position

**Custom Settings** — Add key-value pairs for additional configuration.

## Workflow Examples

### Workflow 1: Find and save the best strategy

1. Go to **Optimize** and select "Auto (all strategies)"
2. Enter your symbols and a long date range (e.g., 2020-2024)
3. Click **Run Optimization** and wait for results
4. Review the recommendation and comparison table
5. Click **Backtest** on the recommended strategy to verify
6. Click **Save as Strategy** to save it

### Workflow 2: Backtest before trading

1. Go to **Strategies** and create a new strategy
2. Go to **Backtest**, enter the same strategy type and parameters
3. Review the performance metrics
4. If satisfied, configure the strategy in the Scheduler for live monitoring

### Workflow 3: Monitor and manage risk

1. Go to **Settings** and enable **Paper Trading** first
2. Set **Max Daily Trades** and **Max Position Size** limits
3. Monitor activity on the **Dashboard**
4. Use the **Kill Switch** if you need to halt everything immediately
