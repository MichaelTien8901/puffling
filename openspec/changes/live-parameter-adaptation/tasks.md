## 1. Data Model

- [ ] 1.1 Create `LiveAdaptationConfig` SQLAlchemy model with fields: id, user_id, strategy_id, trailing_window (default 504), schedule (cron string), max_param_change_pct (default 25), cooldown_days (default 7), confirmation_mode ("auto"/"confirm"), vol_ratio_high (default 1.5), vol_ratio_low (default 0.5), status ("active"/"stopped"), created_at
- [ ] 1.2 Create `AdaptationEvent` SQLAlchemy model with fields: id, config_id, trigger_type ("scheduled"/"regime"), regime_type (nullable), proposed_params JSON, applied_params JSON (nullable), was_capped (bool), status ("applied"/"blocked"/"skipped"/"pending"), reason (nullable), created_at
- [ ] 1.3 Register both models in `backend/models/__init__.py` and ensure table creation

## 2. Regime Detector

- [ ] 2.1 Create `backend/services/regime_detector.py` with `RegimeDetector` class: `compute_volatility_ratio(data, short=20, long=60)` and `compute_trend_strength(data, window=20)`
- [ ] 2.2 Add `detect_regime_change(data, config)` method that checks volatility ratio thresholds and trend sign flips, returns list of regime change events (or empty)

## 3. Live Param Adapter Service

- [ ] 3.1 Create `backend/services/live_adapter_service.py` with `LiveAdapterService` class for CRUD on LiveAdaptationConfig
- [ ] 3.2 Add `run_adaptation(config_id)` method: fetch trailing data, run walk-forward optimization, compute proposed params, enforce change limits (cap at max_param_change_pct of grid range), check kill switch, apply or queue based on confirmation_mode, log AdaptationEvent
- [ ] 3.3 Add parameter change capping logic: for each param, cap delta at `max_param_change_pct / 100 * (grid_max - grid_min)`
- [ ] 3.4 Add cooldown check: skip if last applied event for this config is within cooldown_days
- [ ] 3.5 Add `get_adaptation_history(config_id)` returning AdaptationEvent records ordered by most recent

## 4. Scheduler Integration

- [ ] 4.1 Add APScheduler setup in backend startup (or extend existing scheduler) with support for cron-triggered adaptation jobs
- [ ] 4.2 When a LiveAdaptationConfig is created with status="active", register a cron job that calls `run_adaptation(config_id)`
- [ ] 4.3 When a config is stopped/deleted, remove the corresponding scheduled job
- [ ] 4.4 Add regime detection check as part of scheduled runs: run `detect_regime_change()` before optimization, log regime events, trigger re-optimization if regime changed and cooldown elapsed

## 5. API Endpoints

- [ ] 5.1 Add `POST /api/optimize/live` to create a LiveAdaptationConfig and start scheduling
- [ ] 5.2 Add `DELETE /api/optimize/live/{id}` to stop and deactivate an adaptation config
- [ ] 5.3 Add `GET /api/optimize/live` to list active adaptation configs with status and next run time
- [ ] 5.4 Add `GET /api/optimize/live/{id}/history` to return adaptation event history
- [ ] 5.5 Add WebSocket notifications on `/ws/optimize` for regime changes and adaptation results

## 6. Tests

- [ ] 6.1 Unit tests: RegimeDetector volatility ratio and trend detection with synthetic data
- [ ] 6.2 Unit tests: LiveAdapterService change capping logic, cooldown check, kill-switch blocking
- [ ] 6.3 API tests: CRUD for /api/optimize/live endpoints, history retrieval
- [ ] 6.4 Integration test: scheduled adaptation triggers re-optimization and logs event
