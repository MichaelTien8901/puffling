## 1. Backend — Strategy Recommender Service

- [ ] 1.1 Add `run_strategy_sweep()` method to OptimizerService that iterates over all 4 strategy types, calls existing optimization logic with default grids, and collects per-strategy top-5 results
- [ ] 1.2 Add recommendation scoring: pick global best by mean Sharpe, compute confidence from fold Sharpe std dev (high < 0.3, medium 0.3–0.8, low > 0.8)
- [ ] 1.3 Flag strategy types with negative mean Sharpe as `recommended: false` in results
- [ ] 1.4 Support per-strategy progress callbacks with `{current_strategy, strategy_index, total_strategies, combo, total}`

## 2. Backend — API Endpoint

- [ ] 2.1 Add `POST /api/optimize/sweep` endpoint accepting `{symbols, start, end, n_splits?, train_ratio?}` — creates OptimizationJob with `job_type="sweep"` and runs sweep in background thread
- [ ] 2.2 Ensure `GET /api/optimize/{job_id}` returns sweep-formatted results (by_strategy + recommendation) when job_type is "sweep"
- [ ] 2.3 Add sweep progress to WebSocket `/ws/optimize` with per-strategy fields

## 3. Frontend — Optimize Page Updates

- [ ] 3.1 Add "Auto (all strategies)" option to the strategy type dropdown
- [ ] 3.2 Hide parameter grid section when "Auto" is selected; show note about default grids
- [ ] 3.3 Submit to `/api/optimize/sweep` when "Auto" is selected instead of `/api/optimize/strategy`
- [ ] 3.4 Show per-strategy progress during sweep (strategy N/4 label + combo progress bar)
- [ ] 3.5 Display cross-strategy comparison table when sweep results arrive: one row per strategy type with best Sharpe, best params, mean return, max drawdown, recommended flag
- [ ] 3.6 Add expand/collapse to comparison table rows showing top 5 params per strategy
- [ ] 3.7 Add "Backtest" and "Save as Strategy" action buttons on comparison table rows

## 4. Tests

- [ ] 4.1 Backend unit tests: sweep job creation, per-strategy result aggregation, recommendation scoring, negative Sharpe flagging
- [ ] 4.2 Backend API tests: POST /api/optimize/sweep returns job_id, GET returns sweep results format
- [ ] 4.3 Frontend E2E tests: Auto option hides grid, sweep results show comparison table with strategy rows
