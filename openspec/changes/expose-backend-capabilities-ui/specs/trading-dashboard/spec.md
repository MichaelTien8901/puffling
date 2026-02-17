## ADDED Requirements

### Requirement: Dashboard shows broker account summary
The system SHALL display a panel on the dashboard showing broker account info including cash balance, portfolio value, and buying power.

#### Scenario: Account panel loads on page visit
- **WHEN** user navigates to the dashboard
- **THEN** system calls `GET /api/broker/account` and displays cash, portfolio value, and buying power as stat cards

#### Scenario: Account data unavailable
- **WHEN** the broker account API returns an error (e.g., broker not connected)
- **THEN** the Account panel shows a "Broker not connected" message instead of crashing

### Requirement: Dashboard shows real-time trade feed
The system SHALL display a "Recent Trades" panel on the dashboard that streams live trade executions via WebSocket.

#### Scenario: Trade appears in real-time
- **WHEN** a trade executes while the user is on the dashboard
- **THEN** the trade appears in the Recent Trades panel immediately via `/ws/trades`

#### Scenario: Trade feed shows last 10 trades
- **WHEN** user views the dashboard with trade history
- **THEN** the Recent Trades panel shows the most recent 10 trades with symbol, side, quantity, price, and timestamp

#### Scenario: WebSocket disconnects gracefully
- **WHEN** the `/ws/trades` WebSocket connection drops
- **THEN** the panel shows a "Disconnected" indicator and does not crash
