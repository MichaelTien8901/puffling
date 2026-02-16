## Context

Puffling wraps Puffin's backtesting and strategy infrastructure. Puffin already provides:
- `Backtester` with configurable slippage/commission
- `walk_forward()` with train/test splits and metrics per fold
- 4 strategy types with well-defined parameters via `get_parameters()`
- Ensemble models with `tune_hyperparameters()` (GridSearchCV + TimeSeriesSplit) and `cross_validate()`

Currently users manually set strategy parameters and run single backtests. There is no way to systematically search parameter space or validate robustness across time periods.

## Goals / Non-Goals

**Goals:**
- Let users define parameter ranges and run grid search over strategy params
- Use walk-forward analysis for out-of-sample validation (no overfitting)
- Expose ensemble model tuning (XGBoost, LightGBM, CatBoost, RandomForest)
- Stream progress updates for long-running optimization jobs
- Display ranked results with metrics comparison and one-click best-params apply

**Non-Goals:**
- Bayesian optimization or genetic algorithms (grid search is sufficient for now)
- Auto-selecting strategy type (user chooses which strategy to optimize)
- Real-time parameter adaptation during live trading

## Decisions

### 1. Run optimization as background tasks via existing scheduler

**Choice:** Submit optimization jobs through APScheduler, reusing the `SchedulerService` infrastructure.

**Why:** Optimization can take minutes. Running in the request thread would timeout. The scheduler already handles background async tasks with database persistence.

**Alternative:** Dedicated thread pool — rejected because scheduler already exists and provides job tracking.

### 2. Walk-forward as primary validation method

**Choice:** Use Puffin's `walk_forward(n_splits, train_ratio)` for every parameter combination to get out-of-sample metrics.

**Why:** Single-period backtests overfit. Walk-forward gives multiple train/test splits that reveal parameter robustness. Puffin already implements this.

**Alternative:** Simple train/test split — rejected because it provides only one data point and is more prone to overfitting.

### 3. Rank by Sharpe ratio with secondary sort on max drawdown

**Choice:** Default ranking uses mean test-period Sharpe ratio across walk-forward splits, with max drawdown as tiebreaker.

**Why:** Sharpe captures risk-adjusted return. Users care about both return and drawdown. Configurable via API if needed.

### 4. Strategy param grids defined per strategy type

**Choice:** Provide sensible default parameter grids for each strategy type. Users can override ranges via the UI.

**Default grids:**
- **Momentum:** short_window [5,10,20], long_window [20,50,100], ma_type [sma,ema]
- **Mean Reversion:** window [10,20,30], num_std [1.5,2.0,2.5], zscore_entry [-2.5,-2.0,-1.5]
- **Stat Arb:** lookback [30,60,90], entry_zscore [1.5,2.0,2.5], exit_zscore [0.0,0.5,1.0]
- **Market Making:** spread_bps [5,10,20], max_inventory [50,100,200]

**Why:** Users need reasonable starting points. Grids are small enough to complete in minutes.

### 5. Separate endpoints for strategy optimization vs model tuning

**Choice:** `/api/optimize/strategy` for walk-forward param search, `/api/optimize/model` for ensemble hyperparameter tuning (delegates to Puffin's built-in GridSearchCV).

**Why:** Different inputs (strategy params vs ML hyperparams), different execution paths, different result formats.

### 6. WebSocket for progress streaming

**Choice:** `/ws/optimize` WebSocket channel streams progress (current combo N/total, current fold, intermediate metrics).

**Why:** Optimization can run hundreds of combinations. Users need feedback. Consistent with existing WS pattern (/ws/backtest, /ws/agent).

## Risks / Trade-offs

- **Long run times for large grids** → Cap max combinations (default 500). Show estimated time before starting. Allow cancellation.
- **Memory usage with many walk-forward results** → Store only top-N results (default 20) in database, discard the rest.
- **Walk-forward with small datasets may not have enough data per split** → Validate minimum data length (require at least 252 trading days × n_splits) and warn if insufficient.
- **Ensemble tuning already handled by Puffin** → Our endpoint is a thin wrapper. Risk of API mismatch if Puffin changes — mitigated by Puffin being a local editable install.
