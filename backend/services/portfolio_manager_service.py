import json
import logging

from sqlalchemy.orm import Session

from backend.models.portfolio_goal import PortfolioGoal

logger = logging.getLogger(__name__)


class PortfolioManagerService:
    def __init__(self, db: Session):
        self.db = db

    def create_goal(self, user_id: str, name: str, target_weights: dict, drift_threshold: float = 0.05, rebalance_mode: str = "alert") -> PortfolioGoal:
        goal = PortfolioGoal(
            user_id=user_id, name=name,
            target_weights=json.dumps(target_weights),
            drift_threshold=drift_threshold,
            rebalance_mode=rebalance_mode,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def get_goals(self, user_id: str) -> list[PortfolioGoal]:
        return self.db.query(PortfolioGoal).filter(PortfolioGoal.user_id == user_id).all()

    def get_goal(self, goal_id: int, user_id: str) -> PortfolioGoal | None:
        return self.db.query(PortfolioGoal).filter(
            PortfolioGoal.id == goal_id, PortfolioGoal.user_id == user_id
        ).first()

    def update_goal(self, goal_id: int, user_id: str, **kwargs) -> PortfolioGoal | None:
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return None
        for key, value in kwargs.items():
            if key == "target_weights":
                value = json.dumps(value)
            setattr(goal, key, value)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_goal(self, goal_id: int, user_id: str) -> bool:
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return False
        self.db.delete(goal)
        self.db.commit()
        return True

    def check_drift(self, goal_id: int, user_id: str) -> dict:
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return {"error": "Goal not found"}

        targets = json.loads(goal.target_weights)

        # Get current positions from broker
        try:
            from backend.services.broker_service import BrokerService
            broker = BrokerService(self.db)
            positions = broker.get_positions()
        except Exception:
            positions = []

        # Calculate current weights
        total_value = sum(float(p.get("current_price", 0)) * float(p.get("qty", 0)) for p in positions)
        current_weights = {}
        if total_value > 0:
            for p in positions:
                symbol = p["symbol"]
                value = float(p.get("current_price", 0)) * float(p.get("qty", 0))
                current_weights[symbol] = value / total_value

        # Calculate drift
        drift = {}
        needs_rebalance = False
        for symbol, target in targets.items():
            current = current_weights.get(symbol, 0.0)
            d = abs(current - target)
            drift[symbol] = {"target": target, "current": round(current, 4), "drift": round(d, 4)}
            if d > goal.drift_threshold:
                needs_rebalance = True

        return {
            "goal_id": goal.id,
            "name": goal.name,
            "drift": drift,
            "needs_rebalance": needs_rebalance,
            "threshold": goal.drift_threshold,
            "rebalance_mode": goal.rebalance_mode,
        }

    def rebalance(self, goal_id: int, user_id: str) -> dict:
        drift_info = self.check_drift(goal_id, user_id)
        if drift_info.get("error"):
            return drift_info
        if not drift_info["needs_rebalance"]:
            return {"status": "no rebalance needed"}

        goal = self.get_goal(goal_id, user_id)
        targets = json.loads(goal.target_weights)

        try:
            from puffin.portfolio import RebalanceEngine
            engine = RebalanceEngine()
            current = {s: d["current"] for s, d in drift_info["drift"].items()}
            trades = engine.calculate_trades(current, targets)
            if goal.rebalance_mode == "auto":
                from backend.services.broker_service import BrokerService
                broker = BrokerService(self.db)
                for trade in trades:
                    broker.submit_order(trade.symbol, trade.side, trade.qty)
                return {"status": "rebalance executed", "trades": len(trades)}
            else:
                return {"status": "rebalance suggested", "trades": [t.__dict__ for t in trades]}
        except Exception as e:
            logger.error(f"Rebalance failed: {e}")
            return {"status": "error", "message": str(e)}
