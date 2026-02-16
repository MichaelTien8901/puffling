from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class OptimizationJob(Base):
    __tablename__ = "optimization_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    job_type: Mapped[str] = mapped_column(String)  # "strategy" or "model"
    strategy_type: Mapped[str | None] = mapped_column(String, nullable=True)
    config: Mapped[str] = mapped_column(Text)  # JSON string
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, running, complete, cancelled, error
    results: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
