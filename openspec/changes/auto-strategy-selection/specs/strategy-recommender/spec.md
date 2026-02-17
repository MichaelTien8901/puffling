## ADDED Requirements

### Requirement: Multi-strategy sweep execution
The system SHALL accept a symbol list, date range, and walk-forward settings, then run parameter optimization across all 4 strategy types (momentum, mean_reversion, stat_arb, market_making) using each type's default parameter grid.

#### Scenario: Run sweep for SPY
- **WHEN** user submits a sweep for symbols=["SPY"], date range="2020-01-01 to 2024-12-31"
- **THEN** system runs walk-forward optimization for all 4 strategy types sequentially and returns per-strategy results

#### Scenario: Sweep with custom walk-forward settings
- **WHEN** user submits a sweep with n_splits=3 and train_ratio=0.8
- **THEN** system applies those settings to all 4 strategy type optimizations

### Requirement: Cross-strategy result ranking
The system SHALL rank results globally across all strategy types by mean test Sharpe ratio and identify the best-performing strategy type.

#### Scenario: Global ranking
- **WHEN** sweep completes with results from 4 strategy types
- **THEN** system returns a combined ranking with each result tagged by its strategy_type, sorted by mean Sharpe descending

### Requirement: Strategy recommendation with confidence
The system SHALL produce a recommendation identifying the best strategy type with a confidence metric based on Sharpe consistency across walk-forward folds.

#### Scenario: High-confidence recommendation
- **WHEN** the best strategy type has mean Sharpe=1.5 and low fold-to-fold Sharpe std dev (< 0.3)
- **THEN** recommendation includes strategy_type, best_params, mean_sharpe, and confidence="high"

#### Scenario: Low-confidence recommendation
- **WHEN** the best strategy type has high fold-to-fold Sharpe std dev (> 0.8)
- **THEN** recommendation includes confidence="low" to indicate inconsistent performance

### Requirement: Per-strategy progress tracking
The system SHALL report progress per strategy type during a sweep, including which strategy is currently being evaluated and its combination progress.

#### Scenario: Progress during sweep
- **WHEN** sweep is running momentum (strategy 2 of 4) at combo 10 of 18
- **THEN** progress update includes {current_strategy: "momentum", strategy_index: 2, total_strategies: 4, combo: 10, total: 18}

### Requirement: Negative Sharpe flagging
The system SHALL flag strategy types with negative mean Sharpe as "not recommended" in the results.

#### Scenario: Strategy with negative Sharpe
- **WHEN** market_making produces mean Sharpe=-0.5 for the given symbol
- **THEN** that strategy's results include recommended=false with a note indicating poor fit
