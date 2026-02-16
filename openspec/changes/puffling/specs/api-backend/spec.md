## ADDED Requirements

### Requirement: FastAPI application serves REST endpoints grouped by Puffin domain
The system SHALL expose REST API endpoints organized by Puffin module domain at the following route groups: `/api/data`, `/api/factors`, `/api/strategies`, `/api/backtest`, `/api/portfolio`, `/api/models`, `/api/ai`, `/api/broker`, `/api/risk`, `/api/monitor`, `/api/settings`.

#### Scenario: Health check endpoint responds
- **WHEN** a client sends GET `/api/health`
- **THEN** the system returns HTTP 200 with a JSON body containing `{"status": "ok"}`

#### Scenario: Data endpoint returns OHLCV data
- **WHEN** a client sends GET `/api/data/ohlcv?symbol=AAPL&start=2024-01-01&end=2024-12-31`
- **THEN** the system returns HTTP 200 with OHLCV price data for AAPL from the Puffin DataProvider

#### Scenario: Unknown route returns 404
- **WHEN** a client sends a request to an undefined route
- **THEN** the system returns HTTP 404

### Requirement: WebSocket channels provide real-time streaming
The system SHALL expose WebSocket endpoints for real-time data: `/ws/prices`, `/ws/backtest/{id}`, `/ws/trades`, `/ws/ai/chat`.

#### Scenario: Price streaming via WebSocket
- **WHEN** a client connects to `/ws/prices` and subscribes to symbol "AAPL"
- **THEN** the system streams real-time price updates as JSON messages

#### Scenario: Backtest progress via WebSocket
- **WHEN** a client connects to `/ws/backtest/{id}` for an active backtest
- **THEN** the system streams progress updates and final results

### Requirement: Services are thin wrappers around Puffin modules
The system SHALL implement backend services as thin adapters that instantiate and call Puffin classes without duplicating business logic.

#### Scenario: Backtest service delegates to Puffin Backtester
- **WHEN** a client sends POST `/api/backtest` with strategy config, symbols, and date range
- **THEN** the service instantiates Puffin's `Backtester` class and calls its `run` method
- **AND** the result is persisted to the database and returned to the client

#### Scenario: Strategy service delegates to Puffin strategies
- **WHEN** a client sends POST `/api/strategies/{name}/signals` with parameters
- **THEN** the service instantiates the named Puffin strategy and generates signals without reimplementing strategy logic

### Requirement: All API responses include user context
The system SHALL accept and propagate a user context on all API requests, defaulting to a "default" user in single-user mode.

#### Scenario: Default user is used when no user specified
- **WHEN** a client sends a request without explicit user identification
- **THEN** the system uses the auto-provisioned default user context

#### Scenario: User-scoped data isolation
- **WHEN** a client requests data (e.g., GET `/api/strategies`)
- **THEN** the system returns only data belonging to the requesting user's scope

### Requirement: Models endpoint supports ML, deep learning, ensembles, and RL
The system SHALL expose `/api/models` endpoints that support training and prediction across Puffin's `ml`, `deep`, `ensembles`, and `rl` modules, accepting a model type parameter to select the backend.

#### Scenario: Train an ensemble model
- **WHEN** a client sends POST `/api/models/train` with `{"model_type": "xgboost", ...}`
- **THEN** the service delegates to Puffin's `XGBoostTrader` and returns training metrics

#### Scenario: Train a deep learning model
- **WHEN** a client sends POST `/api/models/train` with `{"model_type": "lstm", ...}`
- **THEN** the service delegates to Puffin's `TradingLSTM` and returns training metrics

#### Scenario: Train an RL agent
- **WHEN** a client sends POST `/api/models/train` with `{"model_type": "dqn", ...}`
- **THEN** the service delegates to Puffin's `DQNAgent` with `TradingEnvironment` and returns episode rewards

#### Scenario: List available model types
- **WHEN** a client sends GET `/api/models/types`
- **THEN** the system returns available model types grouped by category (ml, deep, ensembles, rl)

### Requirement: Factors endpoint includes unsupervised analysis
The system SHALL expose `/api/factors` endpoints that include Puffin's `unsupervised` module for PCA-based risk factor extraction and asset clustering.

#### Scenario: Extract risk factors via PCA
- **WHEN** a client sends POST `/api/factors/risk-factors` with symbol list and date range
- **THEN** the service delegates to Puffin's `MarketPCA` and `extract_risk_factors()` and returns principal components with variance explained

#### Scenario: Cluster assets
- **WHEN** a client sends POST `/api/factors/cluster` with symbol list and method
- **THEN** the service delegates to Puffin's `cluster_assets()` and returns cluster assignments

### Requirement: AI endpoint includes NLP text analysis
The system SHALL expose `/api/ai` endpoints that include Puffin's `nlp` module for topic modeling, financial sentiment lexicons, and document analysis.

#### Scenario: Analyze text sentiment with financial lexicon
- **WHEN** a client sends POST `/api/ai/sentiment` with financial text
- **THEN** the service delegates to Puffin's `nlp.RuleSentiment` (Loughran-McDonald lexicon) and returns sentiment scores

#### Scenario: Extract topics from documents
- **WHEN** a client sends POST `/api/ai/topics` with a collection of text documents
- **THEN** the service delegates to Puffin's `LDAModel` and returns topic distributions

### Requirement: Broker actions require confirmation
The system SHALL NOT execute broker actions (order placement, cancellation) without explicit user confirmation.

#### Scenario: Order placement requires confirmation
- **WHEN** a client sends POST `/api/broker/order` with order details
- **THEN** the system returns a confirmation prompt with order summary
- **AND** the order is only executed after receiving a confirmation follow-up request

#### Scenario: Unconfirmed order is not executed
- **WHEN** a client sends an order request but does not send a confirmation
- **THEN** the order is NOT placed with the broker
