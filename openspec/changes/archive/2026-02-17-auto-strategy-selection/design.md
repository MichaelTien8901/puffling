## Context

Puffling's optimize page currently requires users to select a single strategy type (momentum, mean_reversion, stat_arb, market_making) before running parameter optimization. The `OptimizerService.run_strategy_optimization()` handles one strategy type per job, iterating over parameter grid combinations and running walk-forward validation.

Users exploring a new symbol don't know which strategy type fits best. A multi-strategy sweep would run all 4 strategy types with their default grids, rank results globally by Sharpe ratio, and recommend the best-fit strategy.

## Goals / Non-Goals

**Goals:**
- Run optimization across all 4 strategy types in a single job and rank results globally
- Recommend the best strategy type with comparative metrics
- Show per-strategy progress in the UI during sweep
- Reuse existing `run_strategy_optimization` logic — no duplication

**Non-Goals:**
- Custom per-strategy grids in sweep mode (use defaults only; users can fine-tune after selecting a strategy)
- Parallel execution of strategy types (run sequentially to keep resource usage predictable)
- Bayesian or adaptive search — this uses the same grid search as single-strategy mode

## Decisions

### 1. Single sweep job with sub-results per strategy type

**Decision:** One `OptimizationJob` row with `job_type: "sweep"`. Results JSON contains a `by_strategy` dict keyed by strategy type plus a top-level `recommendation` field.

**Alternatives considered:**
- Separate job per strategy type: Simpler per-job, but harder to track as a unit and present a unified recommendation.
- New DB table for sweeps: Over-engineered for what's essentially a job with richer results.

**Rationale:** Reuses existing job infrastructure. The frontend can parse the structured results to show both per-strategy and global views.

### 2. Sequential strategy execution within sweep

**Decision:** Iterate over strategy types sequentially, calling existing `run_strategy_optimization` logic (extracted to a shared helper) for each.

**Rationale:** Simpler, predictable memory usage, and the existing cancellation mechanism works unchanged. Total run time is ~4x a single strategy but still bounded by grid size limits (500 combos max per strategy).

### 3. Recommendation scoring

**Decision:** Rank by mean Sharpe ratio across walk-forward folds. The top result across all strategies becomes the recommendation. Include a `confidence` field based on consistency across folds (std dev of per-fold Sharpe).

**Rationale:** Sharpe is already the primary ranking metric. Adding consistency (low std dev = high confidence) helps users distinguish between a strategy that's good on average vs. one that's reliably good.

### 4. Frontend: "Auto-select" as a strategy type option

**Decision:** Add an "Auto (all strategies)" option to the strategy type dropdown. When selected, hide the parameter grid (defaults used), show per-strategy progress sections, and display a comparison table in results.

**Rationale:** Minimal UI change — reuses the existing optimize page flow. The comparison table replaces the single results table when in sweep mode.

### 5. API: New endpoint vs. extending existing

**Decision:** Add `POST /api/optimize/sweep` as a new endpoint rather than overloading `POST /api/optimize/strategy`.

**Rationale:** Different request schema (no param_grid), different response shape (by_strategy + recommendation). Separate endpoint is cleaner than conditional logic.

## Risks / Trade-offs

- **[Long run times]** → 4x single-strategy duration. Mitigation: Progress updates per strategy type, existing cancellation support, default grids are small (18-27 combos each).
- **[Market making may not suit all symbols]** → Some strategy types may produce nonsensical results for certain assets. Mitigation: Show all results but flag strategies with negative mean Sharpe as "not recommended".
- **[Results size]** → Storing top-N results for 4 strategies in one JSON blob. Mitigation: Keep top_n=5 per strategy in sweep mode (vs. 20 for single), total ~20 result rows.
