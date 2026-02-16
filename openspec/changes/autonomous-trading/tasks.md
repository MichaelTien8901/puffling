## 1. Database Models

- [x] 1.1 Create ScheduledJob model (job_id, user_id, job_type, schedule, config JSON, enabled)
- [x] 1.2 Create PortfolioGoal model (id, user_id, name, target_weights JSON, drift_threshold, rebalance_mode)
- [x] 1.3 Create AlertConfig model (id, user_id, alert_type, condition JSON, enabled)
- [x] 1.4 Create AlertHistory model (id, user_id, alert_config_id, triggered_at, message)
- [x] 1.5 Create AgentLog model (id, user_id, run_at, report JSON, actions_taken JSON)

## 2. Task Scheduler

- [x] 2.1 Add APScheduler dependency to pyproject.toml
- [x] 2.2 Create SchedulerService that initializes APScheduler with asyncio backend on app startup
- [x] 2.3 Load enabled jobs from database on scheduler start
- [x] 2.4 Implement job CRUD (create, update, enable/disable, delete) with database persistence
- [x] 2.5 Create /api/scheduler routes (GET list, POST create, PUT update, DELETE, GET status)

## 3. Live Strategy Runner

- [x] 3.1 Create StrategyRunnerService supporting monitor, alert, and auto-trade modes
- [x] 3.2 Implement signal generation via Puffin Strategy.generate_signals() on schedule
- [x] 3.3 Implement auto-trade execution with safety check integration
- [x] 3.4 Create /api/strategies/live routes (POST activate, PUT update mode, DELETE deactivate, GET active)

## 4. Portfolio Manager

- [x] 4.1 Create PortfolioManagerService with drift calculation (current vs target weights)
- [x] 4.2 Implement automated rebalancing using Puffin RebalanceEngine with cost modeling
- [x] 4.3 Support alert and auto rebalance modes
- [x] 4.4 Create /api/portfolio/goals routes (CRUD goals, GET drift status)

## 5. Alert System

- [x] 5.1 Create AlertService supporting price, signal, risk, and rebalance alert types
- [x] 5.2 Implement alert condition evaluation in scheduled alert_check jobs
- [x] 5.3 Persist triggered alerts to AlertHistory
- [x] 5.4 Create /ws/alerts WebSocket handler for real-time notifications
- [x] 5.5 Create /api/alerts routes (CRUD configs, GET history)

## 6. Autonomous AI Agent

- [x] 6.1 Create AutonomousAgentService with the 5-step agent loop (gather, analyze, report, suggest, execute)
- [x] 6.2 Integrate Puffin LLMProvider with tool-use for agent analysis
- [x] 6.3 Implement budget controls (max API calls per run, max daily spend)
- [x] 6.4 Persist agent logs and stream activity via /ws/agent WebSocket
- [x] 6.5 Create /api/agent routes (GET logs, POST run, PUT config)

## 7. Safety Controls

- [x] 7.1 Create SafetyService with kill switch, paper trading default, daily trade limit, position size limit
- [x] 7.2 Integrate safety checks into strategy runner and agent execution paths
- [x] 7.3 Create /api/safety routes (GET status, POST kill, PUT settings)

## 8. Frontend — Autonomous Features

- [x] 8.1 Add active strategies panel to Dashboard with mode, last signal, next run
- [x] 8.2 Add portfolio goals panel to Dashboard with drift indicators
- [x] 8.3 Add real-time alert feed to Dashboard via /ws/alerts
- [x] 8.4 Create Agent Activity page with run history, reports, and actions
- [x] 8.5 Add safety controls panel with kill switch to Settings page
- [x] 8.6 Create Scheduler management UI for job CRUD

## 9. Testing

- [x] 9.1 Add tests for scheduler service (job CRUD, persistence)
- [x] 9.2 Add tests for strategy runner (signal generation, mode behavior, safety enforcement)
- [x] 9.3 Add tests for portfolio manager (drift calculation, rebalance trade generation)
- [x] 9.4 Add tests for alert system (condition evaluation, trigger persistence)
- [x] 9.5 Add tests for safety controls (kill switch, limits enforcement)
