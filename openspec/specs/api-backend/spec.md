# api-backend Specification

## Purpose
TBD - created by archiving change autonomous-trading. Update Purpose after archive.
## Requirements
### Requirement: Scheduler management endpoints
The system SHALL expose `/api/scheduler` endpoints for CRUD operations on scheduled jobs, plus start/stop and status.

#### Scenario: Create a scheduled job
- **WHEN** a client sends POST `/api/scheduler` with job type, schedule, and config
- **THEN** the job is created and starts executing on schedule

#### Scenario: Get scheduler status
- **WHEN** a client sends GET `/api/scheduler`
- **THEN** the system returns all jobs with their status, next run time, and last result

### Requirement: Portfolio goals endpoints
The system SHALL expose `/api/portfolio/goals` endpoints for managing target allocations and drift monitoring.

#### Scenario: Create a portfolio goal
- **WHEN** a client sends POST `/api/portfolio/goals` with target weights and drift threshold
- **THEN** the goal is persisted and drift monitoring begins

#### Scenario: Get drift status
- **WHEN** a client sends GET `/api/portfolio/goals/{id}/drift`
- **THEN** the system returns current allocations vs targets with drift percentages

### Requirement: Alert management endpoints
The system SHALL expose `/api/alerts` endpoints for CRUD operations and alert history.

#### Scenario: Get alert history
- **WHEN** a client sends GET `/api/alerts/history`
- **THEN** the system returns triggered alerts ordered by most recent

### Requirement: Agent management endpoints
The system SHALL expose `/api/agent` endpoints for viewing logs, configuring the agent, and triggering manual runs.

#### Scenario: Trigger manual agent run
- **WHEN** a client sends POST `/api/agent/run`
- **THEN** the agent loop executes immediately and returns the report

### Requirement: Safety control endpoints
The system SHALL expose `/api/safety` endpoints for managing safety controls including the kill switch.

#### Scenario: Activate kill switch
- **WHEN** a client sends POST `/api/safety/kill`
- **THEN** all autonomous trading immediately stops and no new trades are placed until manually re-enabled

#### Scenario: Get safety status
- **WHEN** a client sends GET `/api/safety`
- **THEN** the system returns current safety settings (paper mode, kill switch, daily trade limit, position limit)

### Requirement: New WebSocket channels for alerts and agent
The system SHALL expose `/ws/alerts` for real-time alert notifications and `/ws/agent` for live agent activity streaming.

#### Scenario: Alert pushes via WebSocket
- **WHEN** an alert triggers
- **THEN** connected clients on `/ws/alerts` receive the alert message

#### Scenario: Agent activity streams via WebSocket
- **WHEN** the agent is running
- **THEN** connected clients on `/ws/agent` receive activity updates

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

### Requirement: Live adaptation management endpoints
The system SHALL expose `/api/optimize/live` endpoints for starting, stopping, and listing live parameter adaptation configs.

#### Scenario: Start live adaptation
- **WHEN** client POSTs to /api/optimize/live with {strategy_id, trailing_window, schedule, max_param_change_pct}
- **THEN** system returns 200 with {id, status: "active", next_run}

#### Scenario: Stop live adaptation
- **WHEN** client DELETEs /api/optimize/live/{id}
- **THEN** system stops the scheduled adaptation and returns {status: "stopped"}

#### Scenario: List active adaptations
- **WHEN** client GETs /api/optimize/live
- **THEN** system returns array of active adaptation configs with status and next run time

### Requirement: Adaptation history endpoint
The system SHALL expose GET /api/optimize/live/{id}/history to retrieve the adaptation event log for a config.

#### Scenario: Get adaptation history
- **WHEN** client GETs /api/optimize/live/{id}/history
- **THEN** system returns array of AdaptationEvent records ordered by most recent, including trigger type, proposed/applied params, and status

### Requirement: Adaptation WebSocket notifications
The system SHALL send adaptation events (regime changes, re-optimization results, parameter changes) on the existing /ws/optimize WebSocket channel.

#### Scenario: Regime change notification
- **WHEN** a regime change is detected for a strategy with active adaptation
- **THEN** connected clients receive {type: "regime_change", strategy_id, regime_type, value}

#### Scenario: Adaptation result notification
- **WHEN** a re-optimization completes and proposes parameter changes
- **THEN** connected clients receive {type: "adaptation_result", strategy_id, proposed_params, status}

