from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.strategy_runner_service import StrategyRunnerService

router = APIRouter()


class ActivateRequest(BaseModel):
    config_id: int
    mode: str = "monitor"  # monitor, alert, auto-trade


class UpdateModeRequest(BaseModel):
    mode: str


@router.post("/activate")
def activate(req: ActivateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyRunnerService(db)
    return svc.activate(req.config_id, user.id, req.mode)


@router.put("/{config_id}/mode")
def update_mode(config_id: int, req: UpdateModeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyRunnerService(db)
    return svc.activate(config_id, user.id, req.mode)


@router.delete("/{config_id}")
def deactivate(config_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyRunnerService(db)
    return svc.deactivate(config_id, user.id)


@router.get("/active")
def get_active(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyRunnerService(db)
    return svc.get_active(user.id)
