## ADDED Requirements

### Requirement: Strategy optimization endpoint
The system SHALL expose POST /api/optimize/strategy to submit a strategy parameter optimization job. Request body SHALL include strategy_type, symbols, start, end, and optional param_grid, n_splits, train_ratio.

#### Scenario: Submit optimization job
- **WHEN** client POSTs to /api/optimize/strategy with {strategy_type: "momentum", symbols: ["SPY"], start: "2020-01-01", end: "2024-12-31"}
- **THEN** system returns 200 with {job_id, status: "running", total_combinations}

### Requirement: Model tuning endpoint
The system SHALL expose POST /api/optimize/model to submit an ensemble model hyperparameter tuning job. Request body SHALL include model_type, feature_config, and optional param_grid.

#### Scenario: Submit model tuning
- **WHEN** client POSTs to /api/optimize/model with {model_type: "xgboost", symbols: ["SPY"], start: "2020-01-01", end: "2024-12-31"}
- **THEN** system returns 200 with {job_id, status: "running"}

### Requirement: Get optimization results
The system SHALL expose GET /api/optimize/{job_id} to retrieve results for a completed or running optimization job.

#### Scenario: Get completed results
- **WHEN** client GETs /api/optimize/{job_id} for a completed job
- **THEN** system returns 200 with {status: "complete", results: [...ranked results...], best_params: {...}}

#### Scenario: Get running job status
- **WHEN** client GETs /api/optimize/{job_id} for a running job
- **THEN** system returns 200 with {status: "running", progress: {combo: 5, total: 18}}

### Requirement: List optimization jobs
The system SHALL expose GET /api/optimize/ to list all optimization jobs for the current user.

#### Scenario: List jobs
- **WHEN** client GETs /api/optimize/
- **THEN** system returns 200 with array of {id, strategy_type, status, created_at, best_sharpe}

### Requirement: Cancel optimization job
The system SHALL expose DELETE /api/optimize/{job_id} to cancel a running optimization job.

#### Scenario: Cancel running job
- **WHEN** client DELETEs /api/optimize/{job_id} for a running job
- **THEN** system returns 200 with {status: "cancelled"} and stops the job gracefully

### Requirement: Optimization progress WebSocket
The system SHALL expose /ws/optimize WebSocket endpoint for streaming optimization progress updates.

#### Scenario: Connect and receive updates
- **WHEN** client connects to /ws/optimize and an optimization job is running
- **THEN** client receives JSON messages with {job_id, combo, total, fold, n_folds, status}
