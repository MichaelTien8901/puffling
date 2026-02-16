## ADDED Requirements

### Requirement: Users can define portfolio goals with target allocations
The system SHALL allow users to create portfolio goals specifying target weights per symbol and a drift threshold percentage.

#### Scenario: User creates a portfolio goal
- **WHEN** a user creates a goal with targets {SPY: 0.6, AGG: 0.3, GLD: 0.1} and drift threshold 5%
- **THEN** the goal is persisted and the system begins monitoring portfolio drift

### Requirement: System detects portfolio drift against goals
The system SHALL compare current portfolio positions against target allocations and calculate drift for each position.

#### Scenario: Drift detected
- **WHEN** SPY allocation drifts from 60% target to 67%
- **THEN** the system reports a drift of 7% which exceeds the 5% threshold

#### Scenario: No drift
- **WHEN** all positions are within the drift threshold
- **THEN** the system reports no rebalancing needed

### Requirement: Automated rebalancing using Puffin RebalanceEngine
The system SHALL generate rebalance trades using Puffin's `RebalanceEngine` with cost modeling when drift exceeds the threshold.

#### Scenario: Rebalance trades are generated
- **WHEN** drift exceeds the threshold and rebalance_mode is "auto"
- **THEN** the system calculates trades via Puffin's `RebalanceEngine` and executes them through the broker with safety checks

#### Scenario: Rebalance in alert mode
- **WHEN** drift exceeds the threshold and rebalance_mode is "alert"
- **THEN** the system generates a notification with suggested rebalance trades but does NOT execute them

### Requirement: Portfolio goals support CRUD operations
The system SHALL allow users to create, read, update, and delete portfolio goals.

#### Scenario: User updates drift threshold
- **WHEN** a user updates a goal's drift threshold from 5% to 3%
- **THEN** subsequent drift checks use the new threshold
