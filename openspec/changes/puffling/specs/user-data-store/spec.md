## ADDED Requirements

### Requirement: SQLite database with SQLAlchemy ORM
The system SHALL use SQLite as the database engine accessed through SQLAlchemy ORM, requiring zero configuration for personal use.

#### Scenario: Database is created on first run
- **WHEN** the application starts for the first time
- **THEN** the system creates the SQLite database file and all required tables

#### Scenario: Database migrations apply cleanly
- **WHEN** the application starts after a schema update
- **THEN** pending migrations are applied without data loss

### Requirement: All tables carry user_id for multi-user extensibility
The system SHALL include a `user_id` foreign key on all data tables to enable future multi-user isolation.

#### Scenario: Default user is auto-provisioned
- **WHEN** the database is initialized for the first time
- **THEN** a default user record is created with id "default"
- **AND** all subsequently created records are associated with this default user

#### Scenario: Records are scoped by user_id
- **WHEN** the system queries for user data (strategies, backtests, trades, etc.)
- **THEN** results are filtered by the requesting user's user_id

### Requirement: User settings storage
The system SHALL store user settings as key-value pairs with JSON values.

#### Scenario: User saves a setting
- **WHEN** a user saves a setting with key "theme" and value "dark"
- **THEN** the setting is persisted in the settings table with the user's user_id

#### Scenario: User retrieves settings
- **WHEN** a user requests their settings
- **THEN** the system returns all key-value settings for that user

### Requirement: Strategy configuration persistence
The system SHALL persist strategy configurations including name, type, and parameters.

#### Scenario: Strategy config is saved
- **WHEN** a user saves a strategy configuration with name, type, and JSON parameters
- **THEN** the record is persisted with the user's user_id and a generated id

#### Scenario: Strategy configs are listed
- **WHEN** a user requests their strategy configurations
- **THEN** the system returns all strategy configs belonging to that user

### Requirement: Backtest result storage
The system SHALL persist backtest results with associated strategy reference and metrics.

#### Scenario: Backtest result is saved after execution
- **WHEN** a backtest completes
- **THEN** the result metrics are persisted as JSON with a reference to the strategy config and user_id

### Requirement: Trade history storage
The system SHALL record all executed trades with symbol, side, quantity, price, and timestamp.

#### Scenario: Trade is recorded
- **WHEN** a trade is executed via the broker
- **THEN** a trade history record is created with symbol, side, quantity, price, timestamp, and user_id

### Requirement: AI conversation persistence
The system SHALL persist AI chat conversations for session continuity.

#### Scenario: Conversation is saved
- **WHEN** a user has an AI chat conversation
- **THEN** the messages are persisted as JSON with the user's user_id and a timestamp

#### Scenario: Conversation history is retrieved
- **WHEN** a user opens the AI chat
- **THEN** previous conversations are available for review
