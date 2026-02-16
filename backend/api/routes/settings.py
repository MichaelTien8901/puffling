from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.settings_service import SettingsService

router = APIRouter()


class SettingRequest(BaseModel):
    key: str
    value: object


@router.get("/")
def get_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SettingsService(db)
    return svc.get_all(user.id)


@router.get("/{key}")
def get_setting(key: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SettingsService(db)
    value = svc.get(user.id, key)
    if value is not None:
        return {"key": key, "value": value}
    return {"error": "not found"}


@router.put("/")
def set_setting(req: SettingRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SettingsService(db)
    svc.set(user.id, req.key, req.value)
    return {"status": "ok"}


@router.delete("/{key}")
def delete_setting(key: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = SettingsService(db)
    if svc.delete(user.id, key):
        return {"status": "deleted"}
    return {"error": "not found"}
