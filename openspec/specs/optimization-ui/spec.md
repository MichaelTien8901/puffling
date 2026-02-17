## ADDED Requirements

### Requirement: Optimization configuration form
The system SHALL provide a form to configure optimization jobs with strategy type selection, symbol input, date range, and editable parameter grid.

#### Scenario: Configure momentum optimization
- **WHEN** user selects strategy_type="momentum"
- **THEN** form pre-fills default parameter grid (short_window, long_window, ma_type) with editable min/max/step or value lists

#### Scenario: Configure walk-forward settings
- **WHEN** user expands advanced settings
- **THEN** form shows n_splits (default 5) and train_ratio (default 0.7) inputs

### Requirement: Run optimization with progress display
The system SHALL show real-time progress when an optimization job is running, including a progress bar, current combination count, and estimated time remaining.

#### Scenario: Progress bar during optimization
- **WHEN** optimization is running (combo 10 of 18)
- **THEN** UI shows progress bar at 55%, "10/18 combinations", and elapsed time

#### Scenario: Cancellation
- **WHEN** user clicks "Cancel" during a running optimization
- **THEN** UI sends cancel request and shows "Cancelling..." until partial results arrive

### Requirement: Results table with ranking
The system SHALL display optimization results as a sortable table showing rank, parameter values, mean Sharpe, mean return, max drawdown, and win rate.

#### Scenario: View ranked results
- **WHEN** optimization completes
- **THEN** table shows top 20 results sorted by Sharpe ratio with all metrics columns

#### Scenario: Sort by different metric
- **WHEN** user clicks the "Max Drawdown" column header
- **THEN** results re-sort by max drawdown ascending

### Requirement: Apply best parameters
The system SHALL allow users to apply a result's parameters to a strategy config or to a new backtest with one click.

#### Scenario: Apply to new backtest
- **WHEN** user clicks "Backtest" on a result row
- **THEN** system navigates to backtest page pre-filled with those parameters

#### Scenario: Apply to strategy config
- **WHEN** user clicks "Save as Strategy" on a result row
- **THEN** system creates a new strategy config with those parameters and shows confirmation

### Requirement: Optimization history
The system SHALL show a list of past optimization jobs with their status, strategy type, date, and best Sharpe achieved.

#### Scenario: View past optimizations
- **WHEN** user visits the optimize page
- **THEN** page shows list of previous optimization jobs with summary metrics

#### Scenario: Load past results
- **WHEN** user clicks on a past optimization job
- **THEN** full results table is displayed for that job

### Requirement: Auto-select strategy option
The system SHALL provide an "Auto (all strategies)" option in the strategy type dropdown. When selected, the parameter grid section SHALL be hidden since default grids are used.

#### Scenario: Select auto mode
- **WHEN** user selects "Auto (all strategies)" from the strategy type dropdown
- **THEN** parameter grid inputs are hidden and a note indicates default grids will be used for all strategy types

#### Scenario: Switch back to single strategy
- **WHEN** user switches from "Auto (all strategies)" back to "momentum"
- **THEN** parameter grid inputs reappear with momentum's default grid

### Requirement: Per-strategy progress display in sweep mode
The system SHALL show progress for each strategy type during a sweep, including which strategy is currently running and overall sweep progress.

#### Scenario: Sweep progress display
- **WHEN** sweep is running momentum (strategy 2 of 4, combo 10 of 18)
- **THEN** UI shows overall "Strategy 2/4: momentum" label and progress bar for current strategy at 55%

### Requirement: Cross-strategy comparison table
The system SHALL display sweep results as a comparison table showing each strategy type's best Sharpe, best params, mean return, max drawdown, and recommendation status.

#### Scenario: View comparison after sweep
- **WHEN** sweep completes
- **THEN** UI shows a comparison table with one row per strategy type, sorted by Sharpe, with the recommended strategy highlighted

#### Scenario: Expand strategy details
- **WHEN** user clicks on a strategy row in the comparison table
- **THEN** UI expands to show the top 5 parameter combinations for that strategy type

### Requirement: Apply recommendation
The system SHALL allow users to apply the recommended strategy's best parameters directly to a backtest or save as a strategy config.

#### Scenario: Apply recommended to backtest
- **WHEN** user clicks "Backtest" on the recommended strategy
- **THEN** system navigates to backtest page pre-filled with the recommended strategy type and its best parameters
