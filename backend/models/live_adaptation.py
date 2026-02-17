from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class LiveAdaptationConfig(Base):
    __tablename__ = "live_adaptation_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    strategy_id: Mapped[int] = mapped_column(Integer, ForeignKey("strategy_configs.id"))
    trailing_window: Mapped[int] = mapped_column(Integer, default=504)
    schedule: Mapped[str] = mapped_column(String)  # cron expression
    max_param_change_pct: Mapped[float] = mapped_column(Float, default=25.0)
    cooldown_days: Mapped[int] = mapped_column(Integer, default=7)
    confirmation_mode: Mapped[str] = mapped_column(String, default="auto")  # "auto" or "confirm"
    vol_ratio_high: Mapped[float] = mapped_column(Float, default=1.5)
    vol_ratio_low: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[str] = mapped_column(String, default="active")  # "active" or "stopped"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AdaptationEvent(Base):
    __tablename__ = "adaptation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_id: Mapped[int] = mapped_column(Integer, ForeignKey("live_adaptation_configs.id"), index=True)
    trigger_type: Mapped[str] = mapped_column(String)  # "scheduled" or "regime"
    regime_type: Mapped[str | None] = mapped_column(String, nullable=True)
    proposed_params: Mapped[str] = mapped_column(Text)  # JSON
    applied_params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    was_capped: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String)  # "applied", "blocked", "skipped", "pending"
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
