## ADDED Requirements

### Requirement: Multi-strategy dispatch mode
The system SHALL support a sweep job type that dispatches optimization across multiple strategy types using default grids, storing results grouped by strategy type in a single job record.

#### Scenario: Submit sweep job
- **WHEN** a sweep is submitted for symbols=["SPY"], start="2020-01-01", end="2024-12-31"
- **THEN** system creates one OptimizationJob with job_type="sweep", runs all 4 strategy types sequentially, and stores results as {by_strategy: {momentum: [...], mean_reversion: [...],...}, recommendation: {...}}

#### Scenario: Sweep job cancellation
- **WHEN** user cancels a running sweep job during the second strategy type
- **THEN** system stops after the current combination, stores partial results for completed strategies, and marks the job as "cancelled"

#### Scenario: Sweep uses top 5 per strategy
- **WHEN** a sweep completes
- **THEN** system stores the top 5 results per strategy type (not 20) to keep result size manageable
