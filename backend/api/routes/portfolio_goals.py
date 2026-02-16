from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.portfolio_manager_service import PortfolioManagerService

router = APIRouter()


class CreateGoalRequest(BaseModel):
    name: str
    target_weights: dict[str, float]
    drift_threshold: float = 0.05
    rebalance_mode: str = "alert"


class UpdateGoalRequest(BaseModel):
    name: str | None = None
    target_weights: dict[str, float] | None = None
    drift_threshold: float | None = None
    rebalance_mode: str | None = None


@router.get("/")
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    goals = svc.get_goals(user.id)
    return [{"id": g.id, "name": g.name, "target_weights": g.target_weights, "drift_threshold": g.drift_threshold, "rebalance_mode": g.rebalance_mode} for g in goals]


@router.post("/")
def create_goal(req: CreateGoalRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    goal = svc.create_goal(user.id, req.name, req.target_weights, req.drift_threshold, req.rebalance_mode)
    return {"id": goal.id, "name": goal.name}


@router.put("/{goal_id}")
def update_goal(goal_id: int, req: UpdateGoalRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    goal = svc.update_goal(goal_id, user.id, **updates)
    if goal:
        return {"id": goal.id, "name": goal.name, "drift_threshold": goal.drift_threshold}
    return {"error": "not found"}


@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    if svc.delete_goal(goal_id, user.id):
        return {"status": "deleted"}
    return {"error": "not found"}


@router.get("/{goal_id}/drift")
def get_drift(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    return svc.check_drift(goal_id, user.id)


@router.post("/{goal_id}/rebalance")
def rebalance(goal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = PortfolioManagerService(db)
    return svc.rebalance(goal_id, user.id)
