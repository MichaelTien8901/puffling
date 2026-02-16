## 1. Database Model

- [x] 1.1 Create OptimizationJob model (id, user_id, job_type, strategy_type, config JSON, status, results JSON, created_at)
- [x] 1.2 Add migration and register model in __init__.py

## 2. Optimizer Service

- [x] 2.1 Create OptimizerService with default param grids for all 4 strategy types
- [x] 2.2 Implement strategy grid search using walk_forward() with configurable n_splits and train_ratio
- [x] 2.3 Implement result ranking by mean test Sharpe ratio with max drawdown tiebreaker, storing top N
- [x] 2.4 Implement ensemble model tuning wrapping Puffin's tune_hyperparameters() and cross_validate()
- [x] 2.5 Add grid size validation (max 500 combinations) and minimum data length check (252 × n_splits days)
- [x] 2.6 Add job cancellation support with graceful stop after current combination
- [x] 2.7 Integrate progress callback for WebSocket streaming (combo index, fold, metrics)

## 3. API Routes

- [x] 3.1 Create POST /api/optimize/strategy endpoint for submitting strategy optimization jobs
- [x] 3.2 Create POST /api/optimize/model endpoint for submitting model tuning jobs
- [x] 3.3 Create GET /api/optimize/ endpoint to list optimization jobs for current user
- [x] 3.4 Create GET /api/optimize/{job_id} endpoint to get results or status
- [x] 3.5 Create DELETE /api/optimize/{job_id} endpoint to cancel a running job
- [x] 3.6 Register optimize router in main.py

## 4. WebSocket

- [x] 4.1 Create /ws/optimize WebSocket handler for streaming progress updates
- [x] 4.2 Register optimize WebSocket router in main.py

## 5. Frontend — Optimize Page

- [x] 5.1 Create /optimize page with strategy type selector, symbol input, date range, and editable param grid form
- [x] 5.2 Add walk-forward advanced settings (n_splits, train_ratio)
- [x] 5.3 Implement optimization progress display with progress bar and combo counter via /ws/optimize
- [x] 5.4 Implement results table with sortable columns (rank, params, Sharpe, return, drawdown, win rate)
- [x] 5.5 Add "Backtest" and "Save as Strategy" action buttons on result rows
- [x] 5.6 Add optimization history list showing past jobs with status and best Sharpe
- [x] 5.7 Add Optimize link to Sidebar navigation

## 6. Testing

- [x] 6.1 Add tests for OptimizerService (default grids, grid size validation, data length check, result ranking)
- [x] 6.2 Add tests for optimize API routes (submit, list, get results, cancel)
