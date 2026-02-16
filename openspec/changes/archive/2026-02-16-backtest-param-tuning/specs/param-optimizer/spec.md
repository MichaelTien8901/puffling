## ADDED Requirements

### Requirement: Strategy parameter grid search
The system SHALL accept a strategy type, symbol list, date range, and parameter grid, then evaluate every parameter combination using walk-forward analysis via Puffin's `walk_forward()`.

#### Scenario: Run momentum strategy optimization
- **WHEN** user submits optimization for strategy_type="momentum", symbols=["SPY"], date range="2020-01-01 to 2024-12-31", param_grid={short_window: [5,10,20], long_window: [20,50,100], ma_type: ["sma","ema"]}
- **THEN** system evaluates all 18 combinations using walk-forward with 5 splits and returns ranked results sorted by mean test Sharpe ratio

#### Scenario: Run with custom walk-forward settings
- **WHEN** user specifies n_splits=3 and train_ratio=0.8
- **THEN** system uses those values instead of defaults (5 splits, 0.7 ratio)

### Requirement: Default parameter grids per strategy type
The system SHALL provide default parameter grids for all 4 strategy types (momentum, mean_reversion, stat_arb, market_making) so users can optimize without specifying ranges.

#### Scenario: Optimize with defaults
- **WHEN** user submits optimization with strategy_type="mean_reversion" and no param_grid
- **THEN** system uses default grid: window=[10,20,30], num_std=[1.5,2.0,2.5], zscore_entry=[-2.5,-2.0,-1.5]

### Requirement: Result ranking and storage
The system SHALL rank parameter combinations by mean test-period Sharpe ratio (descending), with max drawdown as secondary sort (ascending). Only the top N results (default 20) SHALL be persisted.

#### Scenario: Results ranked correctly
- **WHEN** optimization completes with 50 parameter combinations
- **THEN** results are sorted by mean test Sharpe descending, top 20 stored in database with params, metrics per fold, and aggregate metrics

### Requirement: Ensemble model hyperparameter tuning
The system SHALL support hyperparameter tuning for XGBoost, LightGBM, CatBoost, and RandomForest models by delegating to Puffin's `tune_hyperparameters()` or `cross_validate()` methods.

#### Scenario: Tune XGBoost model
- **WHEN** user submits model tuning for model_type="xgboost" with features and target data
- **THEN** system calls Puffin XGBoostTrader.tune_hyperparameters() with TimeSeriesSplit CV and returns best params and scores

#### Scenario: Tune with custom param grid
- **WHEN** user provides a custom param_grid for LightGBM
- **THEN** system passes that grid to LightGBMTrader.tune_hyperparameters() instead of the default

### Requirement: Grid size cap
The system SHALL reject optimization requests where total parameter combinations exceed a configurable maximum (default 500).

#### Scenario: Grid too large
- **WHEN** user submits a param_grid producing 600 combinations
- **THEN** system returns an error with the combination count and the maximum allowed

### Requirement: Minimum data validation
The system SHALL require at least 252 × n_splits trading days of historical data for walk-forward optimization.

#### Scenario: Insufficient data
- **WHEN** user requests optimization with n_splits=5 but only 800 trading days of data
- **THEN** system returns an error indicating minimum 1260 trading days required

### Requirement: Optimization progress streaming
The system SHALL stream progress updates via WebSocket including current combination index, total combinations, current fold, and intermediate metrics.

#### Scenario: Progress updates during optimization
- **WHEN** optimization is running with 18 combinations
- **THEN** WebSocket sends messages like {"combo": 5, "total": 18, "fold": 3, "n_folds": 5, "status": "running"}

#### Scenario: Completion notification
- **WHEN** optimization finishes
- **THEN** WebSocket sends {"status": "complete", "best_sharpe": 1.45, "total_combos": 18}

### Requirement: Job cancellation
The system SHALL allow cancelling a running optimization job.

#### Scenario: Cancel running optimization
- **WHEN** user sends cancel request for an active optimization job
- **THEN** system stops evaluation after the current combination completes and returns partial results
