from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class PortfolioGoal(Base):
    __tablename__ = "portfolio_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String)
    target_weights: Mapped[str] = mapped_column(Text)  # JSON: {"SPY": 0.6, "AGG": 0.3, "GLD": 0.1}
    drift_threshold: Mapped[float] = mapped_column(Float, default=0.05)
    rebalance_mode: Mapped[str] = mapped_column(String, default="alert")  # "alert" or "auto"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
