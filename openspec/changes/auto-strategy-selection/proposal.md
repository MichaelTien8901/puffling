## Why

Users currently must choose which strategy type to optimize manually. For users unfamiliar with strategy characteristics or when exploring a new symbol, automatically evaluating all strategy types and recommending the best-performing one would save time and surface strategies the user might not have considered.

## What Changes

- Add a "multi-strategy sweep" mode that runs optimization across all 4 strategy types and ranks results globally
- Surface a recommendation of which strategy type works best for the given symbol and time period
- Add an auto-select option in the optimization UI that runs all strategies with default grids and presents a comparative summary

## Capabilities

### New Capabilities
- `strategy-recommender`: Service that runs optimization across multiple strategy types, compares results, and recommends the best-fit strategy with confidence metrics

### Modified Capabilities
- `param-optimizer`: Add multi-strategy dispatch mode alongside single-strategy optimization
- `optimization-ui`: Add "Auto-select" strategy option and cross-strategy comparison view

## Impact

- OptimizerService gains multi-strategy orchestration
- Longer run times when evaluating all 4 strategies (UI should show per-strategy progress)
- Frontend optimize page gains auto-select toggle and comparison table
- Existing single-strategy optimization unchanged
