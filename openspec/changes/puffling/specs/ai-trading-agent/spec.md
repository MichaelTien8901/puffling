## ADDED Requirements

### Requirement: AI agent uses Puffin's LLMProvider with tool-use
The system SHALL use Puffin's `LLMProvider` (Claude or OpenAI) with tool-use/function-calling to invoke Puffin capabilities via the backend API.

#### Scenario: AI invokes market data tool
- **WHEN** a user asks "What's the price of AAPL?"
- **THEN** the AI agent calls the `get_market_data` tool mapped to `/api/data`
- **AND** returns the result in natural language

#### Scenario: AI invokes backtest tool
- **WHEN** a user asks "Backtest moving average crossover on SPY for 2024"
- **THEN** the AI agent calls the `run_backtest` tool with appropriate parameters
- **AND** displays the backtest results in the chat

### Requirement: AI agent has access to defined tool set
The system SHALL expose the following tools to the AI agent: `get_market_data`, `run_backtest`, `analyze_sentiment`, `compute_factors`, `optimize_portfolio`, `place_order`, `check_risk`.

#### Scenario: AI lists available capabilities
- **WHEN** a user asks "What can you do?"
- **THEN** the AI describes its available trading capabilities based on the registered tools

#### Scenario: AI selects appropriate tool for request
- **WHEN** a user asks "What's the risk of my current portfolio?"
- **THEN** the AI agent calls the `check_risk` tool and presents the risk analysis

### Requirement: AI responses stream in real-time
The system SHALL stream AI responses token-by-token via the `/ws/ai/chat` WebSocket channel.

#### Scenario: Response streams incrementally
- **WHEN** the AI generates a response
- **THEN** tokens are sent to the client as they are produced via WebSocket
- **AND** the client displays them incrementally

### Requirement: Broker actions via AI require user confirmation
The system SHALL NOT allow the AI agent to execute broker actions (placing orders, canceling orders) without explicit user confirmation in the UI.

#### Scenario: AI requests order placement with confirmation
- **WHEN** a user asks "Buy 100 shares of AAPL"
- **THEN** the AI presents the order details and a confirmation prompt
- **AND** the order is only submitted after the user explicitly confirms

#### Scenario: User declines AI-proposed order
- **WHEN** the AI proposes an order and the user declines
- **THEN** the order is NOT placed and the AI acknowledges the cancellation

### Requirement: AI conversations are persisted
The system SHALL persist all AI chat messages for session continuity and history review.

#### Scenario: Conversation persists across sessions
- **WHEN** a user closes and reopens the AI chat
- **THEN** previous conversation history is available

### Requirement: Paper trading mode is default
The system SHALL operate in paper trading mode by default, ensuring no real orders are placed unless the user explicitly enables live trading.

#### Scenario: Default mode is paper trading
- **WHEN** the application starts with default settings
- **THEN** all broker interactions use paper trading mode

#### Scenario: User enables live trading
- **WHEN** the user explicitly enables live trading in settings
- **THEN** broker actions interact with the real broker API
- **AND** the UI clearly indicates live trading is active
