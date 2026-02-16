import json
import logging
from datetime import date

from sqlalchemy.orm import Session

from backend.models.settings import Settings
from backend.models.trade_history import TradeHistory

logger = logging.getLogger(__name__)

DEFAULT_SAFETY = {
    "paper_trading": True,
    "kill_switch": False,
    "max_daily_trades": 10,
    "max_position_pct": 0.10,
    "large_order_threshold": 1000.0,
}


class SafetyService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, user_id: str) -> dict:
        row = self.db.query(Settings).filter(
            Settings.user_id == user_id, Settings.key == "safety"
        ).first()
        if row:
            return {**DEFAULT_SAFETY, **json.loads(row.value)}
        return DEFAULT_SAFETY.copy()

    def update_settings(self, user_id: str, updates: dict) -> dict:
        current = self.get_settings(user_id)
        current.update(updates)
        row = self.db.query(Settings).filter(
            Settings.user_id == user_id, Settings.key == "safety"
        ).first()
        if row:
            row.value = json.dumps(current)
        else:
            self.db.add(Settings(user_id=user_id, key="safety", value=json.dumps(current)))
        self.db.commit()
        return current

    def activate_kill_switch(self, user_id: str) -> dict:
        self.update_settings(user_id, {"kill_switch": True})
        logger.warning(f"Kill switch activated for user {user_id}")
        return {"status": "kill_switch_active", "message": "All autonomous trading halted"}

    def deactivate_kill_switch(self, user_id: str) -> dict:
        self.update_settings(user_id, {"kill_switch": False})
        logger.info(f"Kill switch deactivated for user {user_id}")
        return {"status": "kill_switch_inactive"}

    def can_trade(self, user_id: str) -> bool:
        settings = self.get_settings(user_id)

        if settings["kill_switch"]:
            logger.warning("Trade blocked: kill switch active")
            return False

        if settings["paper_trading"]:
            return True  # Paper trades always allowed

        # Check daily trade limit
        today_trades = (
            self.db.query(TradeHistory)
            .filter(
                TradeHistory.user_id == user_id,
                TradeHistory.timestamp >= date.today().isoformat(),
            )
            .count()
        )
        if today_trades >= settings["max_daily_trades"]:
            logger.warning(f"Trade blocked: daily limit ({settings['max_daily_trades']}) reached")
            return False

        return True
