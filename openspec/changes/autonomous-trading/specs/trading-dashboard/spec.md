## ADDED Requirements

### Requirement: Dashboard shows active strategy status
The system SHALL display active live strategies on the dashboard with their mode, last signal, and execution status.

#### Scenario: Active strategies panel
- **WHEN** the user views the dashboard with active live strategies
- **THEN** a panel shows each strategy's name, mode (monitor/alert/auto-trade), last signal, and next scheduled run

### Requirement: Dashboard shows portfolio goal drift
The system SHALL display portfolio goal status with current vs target allocations and drift indicators.

#### Scenario: Portfolio goals panel with drift warning
- **WHEN** a portfolio goal has positions drifting beyond the threshold
- **THEN** the dashboard highlights the drifted positions with visual indicators

### Requirement: Dashboard shows recent alerts
The system SHALL display recent alert notifications in a feed on the dashboard.

#### Scenario: Alert feed updates in real-time
- **WHEN** a new alert triggers while the user is on the dashboard
- **THEN** the alert appears in the feed immediately via WebSocket

### Requirement: Agent activity log page
The system SHALL provide a page to view agent run history, reports, and actions taken.

#### Scenario: User views agent logs
- **WHEN** the user navigates to the agent activity page
- **THEN** the page shows a list of agent runs with timestamps, reports, and actions

### Requirement: Safety controls panel
The system SHALL provide a UI panel for managing safety controls including the kill switch.

#### Scenario: User activates kill switch
- **WHEN** the user clicks the kill switch button
- **THEN** all autonomous trading stops immediately and the UI clearly indicates trading is halted
