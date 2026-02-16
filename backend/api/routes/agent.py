from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.autonomous_agent_service import AutonomousAgentService

router = APIRouter()


class RunRequest(BaseModel):
    max_api_calls: int = 10


@router.get("/logs")
def get_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AutonomousAgentService(db)
    logs = svc.get_logs(user.id)
    return [{"id": l.id, "run_at": str(l.run_at), "report": l.report, "actions_taken": l.actions_taken} for l in logs]


@router.post("/run")
def run_agent(req: RunRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AutonomousAgentService(db)
    return svc.run(user.id, req.max_api_calls)
