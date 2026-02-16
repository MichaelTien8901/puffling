import json

from sqlalchemy.orm import Session

from backend.models.strategy_config import StrategyConfig
from puffin.strategies import get_strategy, list_strategies


class StrategyService:
    def __init__(self, db: Session):
        self.db = db

    def list_types(self) -> list[str]:
        return list_strategies()

    def create_config(self, user_id: str, name: str, strategy_type: str, params: dict) -> StrategyConfig:
        config = StrategyConfig(
            user_id=user_id, name=name, strategy_type=strategy_type, params=json.dumps(params)
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_configs(self, user_id: str) -> list[StrategyConfig]:
        return self.db.query(StrategyConfig).filter(StrategyConfig.user_id == user_id).all()

    def get_config(self, config_id: int, user_id: str) -> StrategyConfig | None:
        return self.db.query(StrategyConfig).filter(
            StrategyConfig.id == config_id, StrategyConfig.user_id == user_id
        ).first()

    def delete_config(self, config_id: int, user_id: str) -> bool:
        config = self.get_config(config_id, user_id)
        if config:
            self.db.delete(config)
            self.db.commit()
            return True
        return False

    def generate_signals(self, strategy_type: str, params: dict, symbols: list[str], start: str, end: str) -> dict:
        strategy = get_strategy(strategy_type, **params)
        from puffin.data import YFinanceProvider
        provider = YFinanceProvider()
        data = provider.get_data(symbols, start=start, end=end)
        signals = strategy.generate_signals(data)
        return {"signals": signals.reset_index().to_dict(orient="records")}
