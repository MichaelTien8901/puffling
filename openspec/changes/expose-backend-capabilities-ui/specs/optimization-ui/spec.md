## ADDED Requirements

### Requirement: Live adaptation management section
The system SHALL provide a collapsible "Live Adaptation" section on the Optimize page to create, list, and stop live parameter adaptation configs.

#### Scenario: View active adaptations
- **WHEN** user expands the Live Adaptation section
- **THEN** system calls `GET /api/optimize/live` and displays a table of active adaptations with strategy name, regime parameters, and next run time

#### Scenario: Create new adaptation
- **WHEN** user fills in the adaptation form (strategy, regime parameters) and clicks "Create"
- **THEN** system calls `POST /api/optimize/live` and the new adaptation appears in the active list

#### Scenario: Stop adaptation
- **WHEN** user clicks "Stop" on an active adaptation row
- **THEN** system calls `DELETE /api/optimize/live/{config_id}` and the adaptation is removed from the list

### Requirement: Adaptation history view
The system SHALL allow users to view the event history for each adaptation config.

#### Scenario: Expand adaptation history
- **WHEN** user clicks on an adaptation row to expand it
- **THEN** system calls `GET /api/optimize/live/{config_id}/history` and displays events with trigger type, proposed params, applied params, and status

#### Scenario: Empty history
- **WHEN** an adaptation has no events yet
- **THEN** the expanded section shows "No adaptation events yet"

### Requirement: Backtest progress indicator
The system SHALL show a progress indicator on the Backtest page while a backtest is running, using the WebSocket endpoint.

#### Scenario: Progress during backtest
- **WHEN** user submits a backtest
- **THEN** system connects to `/ws/backtest/{id}` and shows a progress bar or "Running..." indicator until results arrive

#### Scenario: WebSocket fallback
- **WHEN** the backtest WebSocket connection fails
- **THEN** the page falls back to showing a static "Running..." message until the REST response arrives
