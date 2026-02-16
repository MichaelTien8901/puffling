## ADDED Requirements

### Requirement: Dashboard page displays portfolio summary
The system SHALL render a dashboard at `/` showing portfolio summary, watchlist, and recent trades.

#### Scenario: Dashboard loads with portfolio data
- **WHEN** the user navigates to `/`
- **THEN** the page displays current portfolio value, daily P&L, and a watchlist of tracked symbols

#### Scenario: Dashboard shows recent trades
- **WHEN** the user views the dashboard
- **THEN** the page displays the most recent trades with symbol, side, quantity, price, and timestamp

### Requirement: Backtest page allows strategy configuration and execution
The system SHALL provide a backtest page at `/backtest` with strategy selection, parameter configuration, and interactive results display.

#### Scenario: User runs a backtest
- **WHEN** the user selects a strategy, configures parameters, and clicks "Run Backtest"
- **THEN** the system submits the backtest request and displays a progress indicator
- **AND** upon completion, the results are displayed with equity curve chart and performance metrics

#### Scenario: Backtest results include TradingView chart
- **WHEN** a backtest completes successfully
- **THEN** the results page renders an equity curve using TradingView lightweight-charts

### Requirement: Real-time price charts using TradingView lightweight-charts
The system SHALL render interactive financial charts using the TradingView lightweight-charts library.

#### Scenario: OHLCV candlestick chart renders
- **WHEN** the user views a symbol's chart
- **THEN** the system renders an interactive candlestick chart with zoom, pan, and crosshair

#### Scenario: Chart updates in real-time
- **WHEN** the user is viewing a chart and new price data arrives via WebSocket
- **THEN** the chart updates in real-time without a page refresh

### Requirement: Strategy management page
The system SHALL provide a strategy management page at `/strategies` for viewing, creating, and editing strategy configurations.

#### Scenario: User creates a new strategy config
- **WHEN** the user navigates to `/strategies` and clicks "New Strategy"
- **THEN** the system presents a form for strategy type selection and parameter configuration
- **AND** upon saving, the config is persisted via the API

#### Scenario: User views strategy signals
- **WHEN** the user selects a saved strategy and clicks "View Signals"
- **THEN** the system displays generated trading signals for the configured symbols

### Requirement: AI chat interface
The system SHALL provide an AI chat page at `/ai` for natural language interaction with the trading agent.

#### Scenario: User sends a message to the AI
- **WHEN** the user types a message and sends it
- **THEN** the system streams the AI response in real-time via WebSocket
- **AND** displays the response incrementally in the chat panel

#### Scenario: AI response includes actionable results
- **WHEN** the AI performs an action (e.g., runs a backtest, fetches data)
- **THEN** the chat displays the action result inline (charts, tables, or summaries)

### Requirement: Settings page for app configuration
The system SHALL provide a settings page at `/settings` for managing API keys, preferences, and app configuration.

#### Scenario: User updates API key
- **WHEN** the user enters a new API key and saves
- **THEN** the setting is persisted via the API and used for subsequent requests

### Requirement: Navigation between pages
The system SHALL provide persistent navigation allowing users to switch between all pages.

#### Scenario: User navigates between pages
- **WHEN** the user clicks a navigation link
- **THEN** the corresponding page loads without a full page refresh
