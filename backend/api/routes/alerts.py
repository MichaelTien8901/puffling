from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.alert_service import AlertService

router = APIRouter()


class CreateAlertRequest(BaseModel):
    alert_type: str  # price, signal, risk, rebalance
    condition: dict


class UpdateAlertRequest(BaseModel):
    condition: dict | None = None
    enabled: bool | None = None


@router.get("/")
def list_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AlertService(db)
    alerts = svc.get_alerts(user.id)
    return [{"id": a.id, "alert_type": a.alert_type, "condition": a.condition, "enabled": a.enabled} for a in alerts]


@router.post("/")
def create_alert(req: CreateAlertRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AlertService(db)
    alert = svc.create_alert(user.id, req.alert_type, req.condition)
    return {"id": alert.id, "alert_type": alert.alert_type}


@router.put("/{alert_id}")
def update_alert(alert_id: int, req: UpdateAlertRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AlertService(db)
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    alert = svc.update_alert(alert_id, user.id, **updates)
    if alert:
        return {"id": alert.id, "enabled": alert.enabled}
    return {"error": "not found"}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AlertService(db)
    if svc.delete_alert(alert_id, user.id):
        return {"status": "deleted"}
    return {"error": "not found"}


@router.get("/history")
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = AlertService(db)
    history = svc.get_history(user.id)
    return [{"id": h.id, "message": h.message, "triggered_at": str(h.triggered_at)} for h in history]
