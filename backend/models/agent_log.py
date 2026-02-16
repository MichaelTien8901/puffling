from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    run_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    report: Mapped[str] = mapped_column(Text)  # JSON
    actions_taken: Mapped[str] = mapped_column(Text, default="[]")  # JSON
