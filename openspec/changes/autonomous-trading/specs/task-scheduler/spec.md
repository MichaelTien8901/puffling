## ADDED Requirements

### Requirement: Background job scheduler runs periodic tasks
The system SHALL provide a background job scheduler using APScheduler that executes configured tasks on cron-like schedules within the FastAPI process.

#### Scenario: Scheduler starts with the application
- **WHEN** the FastAPI application starts
- **THEN** the scheduler loads all enabled jobs from the database and begins executing them on schedule

#### Scenario: Scheduler persists jobs across restarts
- **WHEN** the application restarts
- **THEN** previously configured and enabled jobs resume on their defined schedules

### Requirement: Users can create, update, and delete scheduled jobs
The system SHALL allow users to manage scheduled jobs via the API, specifying job type, cron schedule, and configuration parameters.

#### Scenario: User creates a market scan job
- **WHEN** a user creates a job with type "market_scan", schedule "0 9 * * 1-5", and strategy config
- **THEN** the job is persisted and begins running at 9 AM on weekdays

#### Scenario: User disables a job
- **WHEN** a user sets a job's enabled flag to false
- **THEN** the job stops executing but remains in the database for re-enabling

#### Scenario: User deletes a job
- **WHEN** a user deletes a scheduled job
- **THEN** the job is removed from the scheduler and database

### Requirement: Supported job types
The system SHALL support four job types: `market_scan`, `portfolio_check`, `ai_analysis`, and `alert_check`.

#### Scenario: Market scan job generates signals
- **WHEN** a market_scan job executes
- **THEN** the system runs the configured strategy and stores generated signals

#### Scenario: Portfolio check job detects drift
- **WHEN** a portfolio_check job executes
- **THEN** the system compares current positions against target allocations and reports drift

#### Scenario: AI analysis job produces a report
- **WHEN** an ai_analysis job executes
- **THEN** the system invokes the AI agent and stores the generated report

#### Scenario: Alert check job evaluates conditions
- **WHEN** an alert_check job executes
- **THEN** the system evaluates all enabled alert conditions and triggers notifications for met conditions
