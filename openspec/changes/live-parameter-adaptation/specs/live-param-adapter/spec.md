## ADDED Requirements

### Requirement: Live adaptation configuration
The system SHALL allow users to configure live parameter adaptation for a running strategy, specifying trailing window size, re-optimization schedule, parameter change limits, and confirmation mode.

#### Scenario: Create adaptation config
- **WHEN** user creates a live adaptation config with strategy_id, trailing_window=504 days, schedule="0 2 * * SAT", max_param_change_pct=25
- **THEN** system persists the config in LiveAdaptationConfig and begins monitoring on the specified schedule

#### Scenario: Default configuration values
- **WHEN** user creates a config without specifying optional fields
- **THEN** system uses defaults: trailing_window=504, max_param_change_pct=25, cooldown_days=7, confirmation_mode="auto" for paper, "confirm" for live

### Requirement: Scheduled re-optimization
The system SHALL run re-optimization on the trailing data window at the configured schedule using the strategy's default parameter grid and walk-forward validation.

#### Scenario: Scheduled re-optimization triggers
- **WHEN** the cron schedule fires for an active adaptation config
- **THEN** system fetches the trailing window of data, runs walk-forward optimization, and produces proposed parameter changes

#### Scenario: Cooldown prevents re-optimization
- **WHEN** a re-optimization was applied 3 days ago and cooldown_days=7
- **THEN** the scheduled trigger is skipped and logged as "skipped: cooldown active"

### Requirement: Parameter change limits
The system SHALL enforce maximum parameter change limits per adaptation cycle to prevent large sudden shifts.

#### Scenario: Change within limits
- **WHEN** re-optimization proposes short_window change from 10 to 15 (grid range 5-20, 33% change)
- **THEN** system accepts the change since 33% > 25% limit, so it caps at 25% change (10 → 13.75, rounded to 14)

#### Scenario: Change exceeds limits
- **WHEN** re-optimization proposes short_window change from 5 to 20 (100% of grid range)
- **THEN** system caps the change at 25% of range and logs the capping

### Requirement: Kill-switch integration
The system SHALL check the kill switch before applying any parameter changes. If the kill switch is active, proposed changes SHALL be queued but not applied.

#### Scenario: Kill switch blocks adaptation
- **WHEN** re-optimization completes but kill switch is active
- **THEN** system logs the proposed changes as "blocked: kill switch active" and does not apply them

### Requirement: Confirmation modes
The system SHALL support two confirmation modes: "auto" (apply changes immediately) and "confirm" (queue changes for user approval).

#### Scenario: Auto mode applies changes
- **WHEN** confirmation_mode="auto" and re-optimization produces valid changes within limits
- **THEN** system applies the new parameters to the running strategy immediately and logs the event

#### Scenario: Confirm mode queues changes
- **WHEN** confirmation_mode="confirm" and re-optimization produces changes
- **THEN** system creates an alert/notification with proposed changes and waits for user approval

### Requirement: Adaptation event logging
The system SHALL log every adaptation event in the AdaptationEvent table, including trigger type, proposed params, applied params, whether capped, and outcome.

#### Scenario: View adaptation history
- **WHEN** user requests adaptation history for a strategy
- **THEN** system returns chronological list of events with trigger (scheduled/regime), proposed vs applied params, and status (applied/blocked/skipped/pending)
