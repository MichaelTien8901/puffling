## ADDED Requirements

### Requirement: Rolling-window re-optimization mode
The system SHALL support a rolling-window re-optimization mode that runs walk-forward optimization on a trailing data window, using the strategy's existing grid and settings.

#### Scenario: Rolling re-optimization
- **WHEN** a re-optimization is triggered for a strategy with trailing_window=504 days
- **THEN** system fetches the most recent 504 days of data and runs walk-forward optimization with the strategy's default grid

#### Scenario: Insufficient trailing data
- **WHEN** trailing_window=504 but only 300 days of data are available
- **THEN** system logs an error and skips the re-optimization
