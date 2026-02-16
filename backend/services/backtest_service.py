import json

from sqlalchemy.orm import Session

from backend.models.backtest_result import BacktestResult
from puffin.backtest import Backtester
from puffin.data import YFinanceProvider
from puffin.strategies import get_strategy


class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    def run(
        self, user_id: str, strategy_type: str, params: dict,
        symbols: list[str], start: str, end: str, strategy_id: int | None = None,
    ) -> dict:
        strategy = get_strategy(strategy_type, **params)
        provider = YFinanceProvider()
        backtester = Backtester(strategy, provider)
        result = backtester.run(symbols, start, end)
        metrics = result.to_dict() if hasattr(result, "to_dict") else {"summary": str(result)}
        record = BacktestResult(
            user_id=user_id, strategy_id=strategy_id, metrics=json.dumps(metrics)
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return {"id": record.id, "metrics": metrics}

    def get_results(self, user_id: str) -> list[BacktestResult]:
        return self.db.query(BacktestResult).filter(BacktestResult.user_id == user_id).all()

    def get_result(self, result_id: int, user_id: str) -> BacktestResult | None:
        return self.db.query(BacktestResult).filter(
            BacktestResult.id == result_id, BacktestResult.user_id == user_id
        ).first()
