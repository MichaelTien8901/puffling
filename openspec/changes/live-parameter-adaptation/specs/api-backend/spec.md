## ADDED Requirements

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
