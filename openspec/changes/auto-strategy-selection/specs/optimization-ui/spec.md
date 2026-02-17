## ADDED Requirements

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
