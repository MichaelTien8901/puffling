import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models.live_adaptation import AdaptationEvent, LiveAdaptationConfig
from backend.models.strategy_config import StrategyConfig
from backend.services.optimizer_service import DEFAULT_GRIDS, OptimizerService
from backend.services.regime_detector import RegimeDetector
from backend.services.safety_service import SafetyService

logger = logging.getLogger(__name__)


class LiveAdapterService:
    def __init__(self, db: Session):
        self.db = db

    # --- CRUD ---

    def create_config(
        self,
        user_id: str,
        strategy_id: int,
        schedule: str,
        trailing_window: int = 504,
        max_param_change_pct: float = 25.0,
        cooldown_days: int = 7,
        confirmation_mode: str = "auto",
        vol_ratio_high: float = 1.5,
        vol_ratio_low: float = 0.5,
    ) -> LiveAdaptationConfig:
        config = LiveAdaptationConfig(
            user_id=user_id,
            strategy_id=strategy_id,
            schedule=schedule,
            trailing_window=trailing_window,
            max_param_change_pct=max_param_change_pct,
            cooldown_days=cooldown_days,
            confirmation_mode=confirmation_mode,
            vol_ratio_high=vol_ratio_high,
            vol_ratio_low=vol_ratio_low,
            status="active",
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_config(self, config_id: int, user_id: str) -> LiveAdaptationConfig | None:
        return (
            self.db.query(LiveAdaptationConfig)
            .filter(LiveAdaptationConfig.id == config_id, LiveAdaptationConfig.user_id == user_id)
            .first()
        )

    def list_configs(self, user_id: str) -> list[LiveAdaptationConfig]:
        return (
            self.db.query(LiveAdaptationConfig)
            .filter(LiveAdaptationConfig.user_id == user_id)
            .order_by(LiveAdaptationConfig.created_at.desc())
            .all()
        )

    def stop_config(self, config_id: int, user_id: str) -> bool:
        config = self.get_config(config_id, user_id)
        if not config:
            return False
        config.status = "stopped"
        self.db.commit()
        return True

    def get_adaptation_history(self, config_id: int) -> list[AdaptationEvent]:
        return (
            self.db.query(AdaptationEvent)
            .filter(AdaptationEvent.config_id == config_id)
            .order_by(AdaptationEvent.created_at.desc())
            .all()
        )

    # --- Cooldown ---

    def check_cooldown(self, config: LiveAdaptationConfig) -> bool:
        """Return True if cooldown is active (should skip)."""
        last_applied = (
            self.db.query(AdaptationEvent)
            .filter(
                AdaptationEvent.config_id == config.id,
                AdaptationEvent.status == "applied",
            )
            .order_by(AdaptationEvent.created_at.desc())
            .first()
        )
        if not last_applied:
            return False
        cooldown_until = last_applied.created_at + timedelta(days=config.cooldown_days)
        return datetime.utcnow() < cooldown_until

    # --- Parameter capping ---

    @staticmethod
    def cap_params(
        current_params: dict,
        proposed_params: dict,
        param_grid: dict,
        max_change_pct: float,
    ) -> tuple[dict, bool]:
        """Cap parameter changes to max_change_pct of grid range.

        Returns:
            (capped_params, was_capped)
        """
        capped = {}
        was_capped = False
        for key, proposed_val in proposed_params.items():
            current_val = current_params.get(key, proposed_val)
            grid_values = param_grid.get(key, [])

            # For non-numeric or missing grid, pass through
            if not grid_values or not isinstance(proposed_val, (int, float)):
                capped[key] = proposed_val
                continue

            numeric_values = [v for v in grid_values if isinstance(v, (int, float))]
            if not numeric_values:
                capped[key] = proposed_val
                continue

            grid_min = min(numeric_values)
            grid_max = max(numeric_values)
            grid_range = grid_max - grid_min
            if grid_range == 0:
                capped[key] = proposed_val
                continue

            max_delta = (max_change_pct / 100.0) * grid_range
            delta = proposed_val - current_val
            if abs(delta) > max_delta:
                was_capped = True
                sign = 1 if delta > 0 else -1
                capped_val = current_val + sign * max_delta
                # Round to match type
                if isinstance(current_val, int) and isinstance(proposed_val, int):
                    capped_val = round(capped_val)
                capped[key] = capped_val
            else:
                capped[key] = proposed_val

        return capped, was_capped

    # --- Run adaptation ---

    def run_adaptation(
        self,
        config_id: int,
        trigger_type: str = "scheduled",
        regime_type: str | None = None,
    ) -> AdaptationEvent | None:
        """Run a single adaptation cycle for the given config."""
        config = self.db.query(LiveAdaptationConfig).filter(
            LiveAdaptationConfig.id == config_id
        ).first()
        if not config or config.status != "active":
            return None

        # Cooldown check
        if self.check_cooldown(config):
            event = AdaptationEvent(
                config_id=config.id,
                trigger_type=trigger_type,
                regime_type=regime_type,
                proposed_params="{}",
                status="skipped",
                reason="cooldown active",
            )
            self.db.add(event)
            self.db.commit()
            logger.info(f"Adaptation {config_id} skipped: cooldown active")
            return event

        # Get the strategy config
        strategy = self.db.query(StrategyConfig).filter(
            StrategyConfig.id == config.strategy_id
        ).first()
        if not strategy:
            logger.error(f"Strategy {config.strategy_id} not found for adaptation {config_id}")
            return None

        current_params = json.loads(strategy.params) if strategy.params else {}
        param_grid = DEFAULT_GRIDS.get(strategy.strategy_type, {})

        # Fetch trailing data and run optimization
        try:
            from puffin.data import YFinanceProvider
            provider = YFinanceProvider()
            # Use trailing window days back from today
            from datetime import date
            end_date = date.today().isoformat()
            start_date = (date.today() - timedelta(days=config.trailing_window)).isoformat()
            data = provider.get_ohlcv(
                json.loads(strategy.params).get("symbol", "SPY") if strategy.params else "SPY",
                start_date,
                end_date,
            )
        except Exception as e:
            event = AdaptationEvent(
                config_id=config.id,
                trigger_type=trigger_type,
                regime_type=regime_type,
                proposed_params="{}",
                status="skipped",
                reason=f"data fetch error: {e}",
            )
            self.db.add(event)
            self.db.commit()
            return event

        # Run optimization to find best params
        try:
            optimizer = OptimizerService(self.db)
            optimizer.validate_data_length(len(data), 5)

            from puffin.backtest.walk_forward import walk_forward
            from puffin.strategies import get_strategy

            combinations = optimizer._expand_grid(param_grid)
            best_result = None
            for params in combinations:
                strat = get_strategy(strategy.strategy_type, **params)
                folds = walk_forward(strat, data, train_ratio=0.7, n_splits=5)
                if not folds:
                    continue
                mean_sharpe = sum(
                    f["test_metrics"].get("sharpe_ratio", 0) for f in folds
                ) / len(folds)
                if best_result is None or mean_sharpe > best_result[1]:
                    best_result = (params, mean_sharpe)

            if best_result is None:
                event = AdaptationEvent(
                    config_id=config.id,
                    trigger_type=trigger_type,
                    regime_type=regime_type,
                    proposed_params="{}",
                    status="skipped",
                    reason="no valid optimization results",
                )
                self.db.add(event)
                self.db.commit()
                return event

            proposed_params = best_result[0]
        except Exception as e:
            event = AdaptationEvent(
                config_id=config.id,
                trigger_type=trigger_type,
                regime_type=regime_type,
                proposed_params="{}",
                status="skipped",
                reason=f"optimization error: {e}",
            )
            self.db.add(event)
            self.db.commit()
            return event

        # Cap parameters
        capped_params, was_capped = self.cap_params(
            current_params, proposed_params, param_grid, config.max_param_change_pct
        )

        # Kill switch check
        safety = SafetyService(self.db)
        if not safety.can_trade(config.user_id):
            event = AdaptationEvent(
                config_id=config.id,
                trigger_type=trigger_type,
                regime_type=regime_type,
                proposed_params=json.dumps(proposed_params),
                applied_params=None,
                was_capped=was_capped,
                status="blocked",
                reason="kill switch active",
            )
            self.db.add(event)
            self.db.commit()
            logger.warning(f"Adaptation {config_id} blocked: kill switch active")
            return event

        # Apply or queue based on confirmation mode
        if config.confirmation_mode == "auto":
            strategy.params = json.dumps(capped_params)
            self.db.commit()
            status = "applied"
            logger.info(f"Adaptation {config_id} applied: {capped_params}")
        else:
            status = "pending"
            logger.info(f"Adaptation {config_id} pending confirmation: {capped_params}")

        event = AdaptationEvent(
            config_id=config.id,
            trigger_type=trigger_type,
            regime_type=regime_type,
            proposed_params=json.dumps(proposed_params),
            applied_params=json.dumps(capped_params) if status == "applied" else None,
            was_capped=was_capped,
            status=status,
            reason=None,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
