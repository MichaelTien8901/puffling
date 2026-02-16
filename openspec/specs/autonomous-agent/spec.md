# autonomous-agent Specification

## Purpose
TBD - created by archiving change autonomous-trading. Update Purpose after archive.
## Requirements
### Requirement: AI agent runs on a configurable schedule
The system SHALL execute the AI agent loop on a user-configurable schedule (e.g., daily at market open) using the user's own Claude or OpenAI API key.

#### Scenario: Agent runs at scheduled time
- **WHEN** the agent is scheduled for 9:30 AM on weekdays
- **THEN** the agent loop executes at that time using the configured LLM API key

#### Scenario: Agent can be triggered manually
- **WHEN** a user requests a manual agent run via the API
- **THEN** the agent loop executes immediately

### Requirement: Agent loop gathers context, analyzes, and acts
The system SHALL execute the agent loop in five steps: gather context, analyze via LLM, produce report, suggest actions, optionally execute actions.

#### Scenario: Agent produces a market report
- **WHEN** the agent loop executes
- **THEN** it gathers portfolio positions, active signals, recent alerts, and market data
- **AND** sends context to the LLM for analysis
- **AND** stores the generated report in the agent_logs table

#### Scenario: Agent suggests actions
- **WHEN** the agent identifies opportunities or risks
- **THEN** it includes suggested actions (buy/sell/rebalance) in its report

#### Scenario: Agent executes actions when auto-trade enabled
- **WHEN** auto-trade is enabled and the agent suggests a trade that passes safety checks
- **THEN** the trade is executed via the broker

#### Scenario: Agent respects budget controls
- **WHEN** the agent has exceeded its configured max API calls per run
- **THEN** the agent stops making LLM calls and reports what it completed

### Requirement: Agent uses Puffin's tool-use capabilities
The system SHALL provide the AI agent with the same tools available in the chat interface (get_market_data, run_backtest, analyze_sentiment, compute_factors, optimize_portfolio, place_order, check_risk).

#### Scenario: Agent uses tools to gather data
- **WHEN** the agent needs current market data for analysis
- **THEN** it invokes the get_market_data tool via Puffin's LLMProvider tool-use

### Requirement: Agent activity is logged and viewable
The system SHALL persist all agent runs with reports and actions taken, and stream activity to connected clients via `/ws/agent`.

#### Scenario: User reviews agent history
- **WHEN** a user requests agent logs
- **THEN** the system returns all agent runs with reports and actions ordered by most recent

#### Scenario: User watches agent in real-time
- **WHEN** the agent is running and the user has an active `/ws/agent` connection
- **THEN** agent activity (tool calls, analysis steps) streams to the client

