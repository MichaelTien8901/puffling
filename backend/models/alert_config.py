from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class AlertConfig(Base):
    __tablename__ = "alert_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    alert_type: Mapped[str] = mapped_column(String)  # price, signal, risk, rebalance
    condition: Mapped[str] = mapped_column(Text)  # JSON: {"symbol": "AAPL", "above": 200}
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
