## Why

Optimized parameters are static — they reflect what worked historically but may degrade as market conditions change. Live parameter adaptation would continuously re-evaluate strategy parameters on recent data and adjust them automatically, keeping strategies tuned to current market regimes without manual re-optimization.

## What Changes

- Add a rolling re-optimization scheduler that periodically re-runs parameter optimization on a trailing data window
- Implement regime detection to trigger re-optimization when market conditions shift (volatility breakout, trend change)
- Add parameter drift monitoring that alerts when current parameters diverge significantly from what recent optimization suggests
- Add safeguards: parameter change limits per period, confirmation for large shifts, kill-switch integration

## Capabilities

### New Capabilities
- `live-param-adapter`: Background service that monitors strategy performance, detects regime changes, and triggers rolling re-optimization with safety constraints
- `regime-detector`: Market regime classification (trending, mean-reverting, volatile) using rolling statistics to trigger adaptation events

### Modified Capabilities
- `param-optimizer`: Add rolling-window re-optimization mode with trailing data window config
- `api-backend`: Add /api/optimize/live endpoints for starting/stopping live adaptation and viewing adaptation history

## Impact

- Requires running strategies to have associated optimization configs
- New scheduled background jobs for periodic re-evaluation
- Safety-critical: parameter changes affect live trading — requires kill-switch integration and change limits
- New WebSocket events for adaptation notifications
- Depends on backtest-param-tuning being complete (extends OptimizerService)
