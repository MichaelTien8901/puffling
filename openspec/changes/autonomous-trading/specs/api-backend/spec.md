## ADDED Requirements

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
