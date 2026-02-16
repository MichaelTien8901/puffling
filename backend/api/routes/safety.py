from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.safety_service import SafetyService

router = APIRouter()


class SafetyUpdateRequest(BaseModel):
    paper_trading: bool | None = None
    max_daily_trades: int | None = None
    max_position_pct: float | None = None
    large_order_threshold: float | None = None


@router.get("/")
def get_safety(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SafetyService(db)
    return svc.get_settings(user.id)


@router.put("/")
def update_safety(req: SafetyUpdateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SafetyService(db)
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    return svc.update_settings(user.id, updates)


@router.post("/kill")
def kill_switch(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SafetyService(db)
    return svc.activate_kill_switch(user.id)


@router.post("/resume")
def resume(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SafetyService(db)
    return svc.deactivate_kill_switch(user.id)
