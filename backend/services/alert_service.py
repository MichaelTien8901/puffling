import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.alert_config import AlertConfig
from backend.models.alert_history import AlertHistory

logger = logging.getLogger(__name__)

# Connected WebSocket clients for alert notifications
alert_connections: list = []


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, user_id: str, alert_type: str, condition: dict) -> AlertConfig:
        alert = AlertConfig(
            user_id=user_id, alert_type=alert_type,
            condition=json.dumps(condition), enabled=True,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_alerts(self, user_id: str) -> list[AlertConfig]:
        return self.db.query(AlertConfig).filter(AlertConfig.user_id == user_id).all()

    def update_alert(self, alert_id: int, user_id: str, **kwargs) -> AlertConfig | None:
        alert = self.db.query(AlertConfig).filter(
            AlertConfig.id == alert_id, AlertConfig.user_id == user_id
        ).first()
        if not alert:
            return None
        for key, value in kwargs.items():
            if key == "condition":
                value = json.dumps(value)
            setattr(alert, key, value)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def delete_alert(self, alert_id: int, user_id: str) -> bool:
        alert = self.db.query(AlertConfig).filter(
            AlertConfig.id == alert_id, AlertConfig.user_id == user_id
        ).first()
        if not alert:
            return False
        self.db.delete(alert)
        self.db.commit()
        return True

    def get_history(self, user_id: str, limit: int = 50) -> list[AlertHistory]:
        return (
            self.db.query(AlertHistory)
            .filter(AlertHistory.user_id == user_id)
            .order_by(AlertHistory.triggered_at.desc())
            .limit(limit)
            .all()
        )

    def evaluate_alerts(self, user_id: str) -> list[dict]:
        alerts = self.db.query(AlertConfig).filter(
            AlertConfig.user_id == user_id, AlertConfig.enabled.is_(True)
        ).all()

        triggered = []
        for alert in alerts:
            condition = json.loads(alert.condition)
            result = self._evaluate_condition(alert.alert_type, condition)
            if result["triggered"]:
                history = AlertHistory(
                    user_id=user_id, alert_config_id=alert.id,
                    message=result["message"],
                )
                self.db.add(history)
                triggered.append({"alert_id": alert.id, "type": alert.alert_type, "message": result["message"]})

        if triggered:
            self.db.commit()
        return triggered

    def _evaluate_condition(self, alert_type: str, condition: dict) -> dict:
        if alert_type == "price":
            return self._check_price(condition)
        elif alert_type == "risk":
            return self._check_risk(condition)
        return {"triggered": False, "message": ""}

    def _check_price(self, condition: dict) -> dict:
        symbol = condition.get("symbol", "")
        try:
            from puffin.data import YFinanceProvider
            provider = YFinanceProvider()
            import datetime
            end = datetime.date.today().isoformat()
            start = (datetime.date.today() - datetime.timedelta(days=5)).isoformat()
            data = provider.get_data(symbol, start=start, end=end)
            current_price = float(data["Close"].iloc[-1])

            if "above" in condition and current_price > condition["above"]:
                return {"triggered": True, "message": f"{symbol} is at ${current_price:.2f}, above ${condition['above']}"}
            if "below" in condition and current_price < condition["below"]:
                return {"triggered": True, "message": f"{symbol} is at ${current_price:.2f}, below ${condition['below']}"}
        except Exception as e:
            logger.error(f"Price check failed: {e}")
        return {"triggered": False, "message": ""}

    def _check_risk(self, condition: dict) -> dict:
        # Placeholder for risk threshold checking
        return {"triggered": False, "message": ""}
