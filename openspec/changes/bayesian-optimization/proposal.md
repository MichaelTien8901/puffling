## Why

Grid search evaluates every parameter combination exhaustively, which becomes impractical as parameter spaces grow. Bayesian optimization (e.g., Optuna/Tree-Parzen Estimators) and genetic algorithms can find good parameters in far fewer evaluations by learning from previous trials, enabling exploration of larger and continuous parameter spaces.

## What Changes

- Add Bayesian optimization as an alternative search method alongside grid search in OptimizerService
- Support continuous parameter ranges (min/max/step) in addition to discrete value lists
- Add genetic algorithm option for multi-objective optimization (Sharpe + drawdown simultaneously)
- Extend the optimization UI to select search method and configure method-specific settings (n_trials, population_size, etc.)

## Capabilities

### New Capabilities
- `bayesian-search`: Bayesian optimization engine using Optuna for efficient parameter search with surrogate models and early stopping
- `genetic-search`: Multi-objective genetic algorithm for Pareto-optimal parameter discovery

### Modified Capabilities
- `param-optimizer`: Add search method selection (grid, bayesian, genetic) and continuous range support
- `optimization-ui`: Add search method selector, method-specific config, and convergence plot visualization

## Impact

- New dependency: `optuna` for Bayesian optimization
- OptimizerService gains new search method dispatch
- Frontend optimize page gains method selector and convergence chart
- Existing grid search behavior unchanged (backward compatible)
