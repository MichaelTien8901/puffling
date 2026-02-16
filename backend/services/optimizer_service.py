import itertools
import json
import threading
from typing import Callable

from sqlalchemy.orm import Session

from backend.models.optimization_job import OptimizationJob
from puffin.backtest.walk_forward import walk_forward
from puffin.data import YFinanceProvider
from puffin.strategies import get_strategy


DEFAULT_GRIDS = {
    "momentum": {
        "short_window": [5, 10, 20],
        "long_window": [20, 50, 100],
        "ma_type": ["sma", "ema"],
    },
    "mean_reversion": {
        "window": [10, 20, 30],
        "num_std": [1.5, 2.0, 2.5],
        "zscore_entry": [-2.5, -2.0, -1.5],
    },
    "stat_arb": {
        "lookback": [30, 60, 90],
        "entry_zscore": [1.5, 2.0, 2.5],
        "exit_zscore": [0.0, 0.5, 1.0],
    },
    "market_making": {
        "spread_bps": [5, 10, 20],
        "max_inventory": [50, 100, 200],
    },
}

MAX_COMBINATIONS = 500
MIN_DAYS_PER_SPLIT = 252

# Track cancellation flags by job_id
_cancel_flags: dict[int, threading.Event] = {}


class OptimizerService:
    def __init__(self, db: Session):
        self.db = db

    def get_default_grid(self, strategy_type: str) -> dict:
        return DEFAULT_GRIDS.get(strategy_type, {})

    def _expand_grid(self, param_grid: dict) -> list[dict]:
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        return [dict(zip(keys, combo)) for combo in itertools.product(*values)]

    def validate_grid_size(self, param_grid: dict) -> int:
        combos = 1
        for values in param_grid.values():
            combos *= len(values)
        if combos > MAX_COMBINATIONS:
            raise ValueError(
                f"Grid produces {combos} combinations, exceeds maximum of {MAX_COMBINATIONS}"
            )
        return combos

    def validate_data_length(self, data_len: int, n_splits: int) -> None:
        min_required = MIN_DAYS_PER_SPLIT * n_splits
        if data_len < min_required:
            raise ValueError(
                f"Insufficient data: {data_len} days, need at least {min_required} "
                f"({MIN_DAYS_PER_SPLIT} × {n_splits} splits)"
            )

    def run_strategy_optimization(
        self,
        job_id: int,
        user_id: str,
        strategy_type: str,
        symbols: list[str],
        start: str,
        end: str,
        param_grid: dict | None = None,
        n_splits: int = 5,
        train_ratio: float = 0.7,
        top_n: int = 20,
        progress_callback: Callable | None = None,
    ) -> list[dict]:
        if param_grid is None:
            param_grid = self.get_default_grid(strategy_type)

        total_combos = self.validate_grid_size(param_grid)
        combinations = self._expand_grid(param_grid)

        # Fetch data
        provider = YFinanceProvider()
        data = provider.get_ohlcv(symbols[0], start, end)
        self.validate_data_length(len(data), n_splits)

        # Set up cancellation
        cancel_event = threading.Event()
        _cancel_flags[job_id] = cancel_event

        # Update job status to running
        job = self.db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job:
            job.status = "running"
            self.db.commit()

        results = []
        try:
            for idx, params in enumerate(combinations):
                if cancel_event.is_set():
                    break

                strategy = get_strategy(strategy_type, **params)
                folds = walk_forward(
                    strategy, data, train_ratio=train_ratio, n_splits=n_splits
                )

                if not folds:
                    continue

                # Aggregate test metrics across folds
                test_sharpes = [f["test_metrics"].get("sharpe_ratio", 0) for f in folds]
                test_returns = [f["test_metrics"].get("total_return", 0) for f in folds]
                test_drawdowns = [f["test_metrics"].get("max_drawdown", 0) for f in folds]
                test_win_rates = [f["test_metrics"].get("win_rate", 0) for f in folds]

                mean_sharpe = sum(test_sharpes) / len(test_sharpes)
                mean_return = sum(test_returns) / len(test_returns)
                max_drawdown = min(test_drawdowns)
                mean_win_rate = sum(test_win_rates) / len(test_win_rates)

                results.append({
                    "params": params,
                    "mean_sharpe": mean_sharpe,
                    "mean_return": mean_return,
                    "max_drawdown": max_drawdown,
                    "mean_win_rate": mean_win_rate,
                    "folds": len(folds),
                })

                if progress_callback:
                    progress_callback({
                        "job_id": job_id,
                        "combo": idx + 1,
                        "total": total_combos,
                        "status": "running",
                    })

            # Rank: best Sharpe desc, then least drawdown (most negative = worst)
            results.sort(key=lambda r: (-r["mean_sharpe"], r["max_drawdown"]))
            results = results[:top_n]

            # Add rank
            for i, r in enumerate(results):
                r["rank"] = i + 1

            # Update job
            status = "cancelled" if cancel_event.is_set() else "complete"
            if job:
                job.status = status
                job.results = json.dumps(results)
                self.db.commit()

            if progress_callback:
                best_sharpe = results[0]["mean_sharpe"] if results else 0
                progress_callback({
                    "job_id": job_id,
                    "status": status,
                    "best_sharpe": best_sharpe,
                    "total_combos": total_combos,
                })

        except Exception as e:
            if job:
                job.status = "error"
                job.results = json.dumps({"error": str(e)})
                self.db.commit()
            raise
        finally:
            _cancel_flags.pop(job_id, None)

        return results

    def run_model_tuning(
        self,
        job_id: int,
        user_id: str,
        model_type: str,
        symbols: list[str],
        start: str,
        end: str,
        param_grid: dict | None = None,
        progress_callback: Callable | None = None,
    ) -> dict:
        from puffin.data import YFinanceProvider
        from puffin.features import FeatureEngineer

        job = self.db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job:
            job.status = "running"
            self.db.commit()

        try:
            provider = YFinanceProvider()
            data = provider.get_ohlcv(symbols[0], start, end)

            engineer = FeatureEngineer()
            features = engineer.create_features(data)
            features = features.dropna()

            X = features.drop(columns=["target"], errors="ignore")
            y = (data["Close"].pct_change().shift(-1) > 0).astype(int).reindex(X.index).dropna()
            X = X.loc[y.index]

            # Get the model class and tune
            if model_type == "xgboost":
                from puffin.ensembles.xgboost_model import XGBoostTrader
                model = XGBoostTrader()
            elif model_type == "lightgbm":
                from puffin.ensembles.lightgbm_model import LightGBMTrader
                model = LightGBMTrader()
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            kwargs = {}
            if param_grid:
                kwargs["param_grid"] = param_grid

            result = model.tune_hyperparameters(X, y, **kwargs)

            if job:
                job.status = "complete"
                # Ensure result is JSON serializable
                serializable = {}
                for k, v in result.items():
                    try:
                        json.dumps(v)
                        serializable[k] = v
                    except (TypeError, ValueError):
                        serializable[k] = str(v)
                job.results = json.dumps(serializable)
                self.db.commit()

            if progress_callback:
                progress_callback({"job_id": job_id, "status": "complete"})

            return result

        except Exception as e:
            if job:
                job.status = "error"
                job.results = json.dumps({"error": str(e)})
                self.db.commit()
            raise

    def cancel_job(self, job_id: int) -> bool:
        event = _cancel_flags.get(job_id)
        if event:
            event.set()
            return True
        # If not running in memory, just update DB status
        job = self.db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job and job.status == "running":
            job.status = "cancelled"
            self.db.commit()
            return True
        return False

    def list_jobs(self, user_id: str) -> list[OptimizationJob]:
        return (
            self.db.query(OptimizationJob)
            .filter(OptimizationJob.user_id == user_id)
            .order_by(OptimizationJob.created_at.desc())
            .all()
        )

    def get_job(self, job_id: int, user_id: str) -> OptimizationJob | None:
        return (
            self.db.query(OptimizationJob)
            .filter(OptimizationJob.id == job_id, OptimizationJob.user_id == user_id)
            .first()
        )
