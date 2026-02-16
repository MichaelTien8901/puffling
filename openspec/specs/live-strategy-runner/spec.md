# live-strategy-runner Specification

## Purpose
TBD - created by archiving change autonomous-trading. Update Purpose after archive.
## Requirements
### Requirement: Strategies can be configured in three execution modes
The system SHALL support three modes for each active strategy: `monitor` (generate signals only), `alert` (signals + notifications), and `auto-trade` (signals + execution with safety checks).

#### Scenario: Monitor mode generates signals without action
- **WHEN** a strategy runs in monitor mode and generates a buy signal
- **THEN** the signal is logged but no alert is sent and no order is placed

#### Scenario: Alert mode notifies on signals
- **WHEN** a strategy runs in alert mode and generates a buy signal
- **THEN** the system sends a real-time notification to the user via WebSocket

#### Scenario: Auto-trade mode executes trades
- **WHEN** a strategy runs in auto-trade mode and generates a buy signal
- **THEN** the system places the order via the broker after passing all safety checks

#### Scenario: Auto-trade mode respects safety controls
- **WHEN** a strategy generates a trade that exceeds position size limits
- **THEN** the order is NOT placed and a safety violation alert is generated

### Requirement: Live strategy execution uses Puffin's strategy framework
The system SHALL delegate signal generation to Puffin's `Strategy.generate_signals()` method without reimplementing strategy logic.

#### Scenario: Strategy runner uses configured Puffin strategy
- **WHEN** a live strategy is scheduled to run
- **THEN** the system instantiates the named Puffin strategy with user-configured parameters and calls `generate_signals()`

