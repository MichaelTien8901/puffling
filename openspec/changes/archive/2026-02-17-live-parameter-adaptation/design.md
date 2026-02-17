## Context

Optimized strategy parameters are static snapshots of what worked historically. Market conditions change — volatility regimes shift, trends emerge or fade — and previously optimal parameters can degrade. Currently, users must manually re-run optimization to re-tune parameters.

The `OptimizerService` already supports walk-forward optimization with configurable windows. This change adds a background scheduler that periodically re-optimizes on trailing data and a regime detector that triggers re-optimization when market conditions shift significantly.

## Goals / Non-Goals

**Goals:**
- Periodically re-optimize strategy parameters on a rolling trailing window
- Detect regime changes (volatility, trend) to trigger on-demand re-optimization
- Monitor parameter drift and alert when current params diverge from optimal
- Enforce safety: parameter change limits, kill-switch integration, confirmation for large shifts

**Non-Goals:**
- Real-time (tick-level) parameter adjustment — this operates on daily data at scheduled intervals
- Automatic parameter application without user confirmation in live trading mode (paper mode can auto-apply)
- Custom regime detection models — use simple rolling statistics (volatility ratio, trend strength)

## Decisions

### 1. Scheduler: APScheduler with cron triggers

**Decision:** Use APScheduler (already lightweight, no external deps) with cron-style scheduling for periodic re-optimization jobs. Store schedule configs in the existing `ScheduledJob` table.

**Alternatives considered:**
- Celery/Redis: Heavy for a single-user app with infrequent jobs.
- Simple threading.Timer: No cron syntax, no persistence, harder to manage.

**Rationale:** APScheduler is stdlib-friendly, supports cron expressions, and can persist job state. Fits the single-user desktop app model.

### 2. Regime detection: Rolling statistics with threshold triggers

**Decision:** Compute rolling volatility ratio (current vol / historical vol) and trend strength (slope of rolling MA). Trigger re-optimization when either metric crosses configurable thresholds.

**Metrics:**
- `volatility_ratio`: 20-day realized vol / 60-day realized vol. Trigger when > 1.5 or < 0.5
- `trend_strength`: Linear regression slope of 20-day close prices, normalized. Trigger when sign changes.

**Alternatives considered:**
- Hidden Markov Models: More sophisticated but harder to tune and explain.
- ML-based regime classification: Over-engineered for triggering re-optimization.

**Rationale:** Simple, interpretable, and sufficient to detect meaningful regime shifts. Users can adjust thresholds.

### 3. Parameter drift monitoring

**Decision:** After each re-optimization, compare new optimal params to currently active params. Compute a normalized distance metric. Alert if drift exceeds a configurable threshold.

**Distance metric:** For each parameter, `|new - current| / range_in_grid`. Average across all parameters. Alert if > 0.5 (parameters shifted by more than half the grid range on average).

### 4. Safety constraints

**Decision:**
- **Max parameter change per period:** Limit how much any single parameter can change in one adaptation cycle (e.g., max 25% of grid range per cycle).
- **Kill-switch integration:** Check `SafetyService.can_trade()` before applying any parameter changes.
- **Confirmation modes:** Paper mode auto-applies. Live mode queues changes for user confirmation via alert/notification.

### 5. Data model: LiveAdaptationConfig + AdaptationEvent

**Decision:** Two new tables:
- `LiveAdaptationConfig`: Links a running strategy to adaptation settings (trailing window, schedule, thresholds, change limits)
- `AdaptationEvent`: Log of each re-optimization trigger (scheduled or regime-triggered), proposed params, whether applied, reason

**Rationale:** Clean audit trail. Users can review what adaptations happened and why.

### 6. API structure

**Decision:** New endpoints under `/api/optimize/live`:
- `POST /api/optimize/live` — Start live adaptation for a strategy
- `DELETE /api/optimize/live/{id}` — Stop live adaptation
- `GET /api/optimize/live` — List active adaptations
- `GET /api/optimize/live/{id}/history` — Adaptation event history

WebSocket events on existing `/ws/optimize` channel for adaptation notifications.

## Risks / Trade-offs

- **[Over-fitting to recent data]** → Short trailing windows may chase noise. Mitigation: Minimum trailing window of 1 year (252 days), walk-forward validation still applied.
- **[Parameter whiplash]** → Frequent regime triggers causing constant parameter changes. Mitigation: Cooldown period between adaptations (default: 7 days), max change limits per cycle.
- **[Safety-critical]** → Automated parameter changes affect live trading. Mitigation: Kill-switch integration, live mode requires confirmation, audit trail in AdaptationEvent table.
- **[Resource usage]** → Background re-optimization jobs consume CPU. Mitigation: Run during off-market hours (configurable), limit to one concurrent adaptation job.
