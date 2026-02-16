## Why

Strategy parameters (moving average windows, z-score thresholds, spread widths) are currently set manually with no guidance on what values work well for a given symbol and time period. Users need a way to automatically search for reasonable parameter combinations using historical data, validated with walk-forward analysis to avoid overfitting.

## What Changes

- Add a parameter optimization service that runs grid search over strategy parameters using Puffin's `walk_forward()` for out-of-sample validation
- Support all 4 strategy types: momentum (short/long window, MA type), mean reversion (window, num_std, z-score thresholds), stat arb (lookback, entry/exit z-score), market making (spread, max inventory)
- Add ensemble model hyperparameter tuning endpoint wrapping Puffin's `tune_hyperparameters()` (XGBoost, LightGBM) and `cross_validate()` (CatBoost, RandomForest)
- Expose optimization results with ranked parameter sets, metrics comparison, and best-params auto-fill
- Add frontend UI for configuring and running parameter sweeps with progress tracking and results visualization

## Capabilities

### New Capabilities
- `param-optimizer`: Backend service for strategy parameter grid search with walk-forward validation and model hyperparameter tuning
- `optimization-ui`: Frontend page for configuring parameter ranges, running optimization jobs, viewing ranked results, and applying best parameters

### Modified Capabilities
- `api-backend`: Add /api/optimize routes for parameter optimization and model tuning

## Impact

- New backend service + API routes under /api/optimize
- New frontend page at /optimize with link in sidebar
- WebSocket channel /ws/optimize for streaming progress during long-running sweeps
- Depends on existing Puffin: `walk_forward()`, `Backtester`, strategy `get_parameters()`, ensemble `tune_hyperparameters()`/`cross_validate()`
- Long-running optimization jobs will use the existing scheduler infrastructure for background execution
