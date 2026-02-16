import json
import logging

from sqlalchemy.orm import Session

from backend.models.strategy_config import StrategyConfig

logger = logging.getLogger(__name__)


class StrategyRunnerService:
    def __init__(self, db: Session):
        self.db = db

    def activate(self, config_id: int, user_id: str, mode: str = "monitor") -> dict:
        config = self.db.query(StrategyConfig).filter(
            StrategyConfig.id == config_id, StrategyConfig.user_id == user_id
        ).first()
        if not config:
            return {"error": "Strategy config not found"}
        # Store mode in params
        params = json.loads(config.params)
        params["_live_mode"] = mode
        config.params = json.dumps(params)
        self.db.commit()
        return {"id": config.id, "name": config.name, "mode": mode, "status": "active"}

    def deactivate(self, config_id: int, user_id: str) -> dict:
        config = self.db.query(StrategyConfig).filter(
            StrategyConfig.id == config_id, StrategyConfig.user_id == user_id
        ).first()
        if not config:
            return {"error": "Strategy config not found"}
        params = json.loads(config.params)
        params.pop("_live_mode", None)
        config.params = json.dumps(params)
        self.db.commit()
        return {"id": config.id, "status": "deactivated"}

    def get_active(self, user_id: str) -> list[dict]:
        configs = self.db.query(StrategyConfig).filter(StrategyConfig.user_id == user_id).all()
        active = []
        for c in configs:
            params = json.loads(c.params)
            if "_live_mode" in params:
                active.append({
                    "id": c.id, "name": c.name, "strategy_type": c.strategy_type,
                    "mode": params["_live_mode"],
                })
        return active

    def run_signal_check(self, config_id: int, user_id: str) -> dict:
        config = self.db.query(StrategyConfig).filter(
            StrategyConfig.id == config_id, StrategyConfig.user_id == user_id
        ).first()
        if not config:
            return {"error": "not found"}

        params = json.loads(config.params)
        mode = params.get("_live_mode", "monitor")
        strategy_params = {k: v for k, v in params.items() if not k.startswith("_")}

        from puffin.strategies import get_strategy
        from puffin.data import YFinanceProvider

        strategy = get_strategy(config.strategy_type, **strategy_params)
        provider = YFinanceProvider()
        # Use recent data
        import datetime
        end = datetime.date.today().isoformat()
        start = (datetime.date.today() - datetime.timedelta(days=90)).isoformat()
        symbols = params.get("_symbols", ["SPY"])
        data = provider.get_data(symbols, start=start, end=end)
        signals = strategy.generate_signals(data)

        result = {"signals": signals.tail(1).to_dict(orient="records"), "mode": mode}

        if mode == "alert" and len(result["signals"]) > 0:
            logger.info(f"Signal alert for strategy {config.name}: {result['signals']}")

        if mode == "auto-trade" and len(result["signals"]) > 0:
            from backend.services.safety_service import SafetyService
            safety = SafetyService(self.db)
            if safety.can_trade(user_id):
                from backend.services.broker_service import BrokerService
                broker = BrokerService(self.db)
                for sig in result["signals"]:
                    if sig.get("signal", 0) > 0:
                        broker.submit_order(sig.get("symbol", symbols[0]), "buy", 1)
                    elif sig.get("signal", 0) < 0:
                        broker.submit_order(sig.get("symbol", symbols[0]), "sell", 1)
                result["trades_submitted"] = True
            else:
                result["trades_submitted"] = False
                result["safety_blocked"] = True

        return result
