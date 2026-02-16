from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.strategy_service import StrategyService

router = APIRouter()


class CreateStrategyRequest(BaseModel):
    name: str
    strategy_type: str
    params: dict = {}


class GenerateSignalsRequest(BaseModel):
    params: dict = {}
    symbols: list[str]
    start: str
    end: str


@router.get("/types")
def list_types():
    return StrategyService(None).list_types()


@router.get("/")
def list_configs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyService(db)
    configs = svc.get_configs(user.id)
    return [{"id": c.id, "name": c.name, "strategy_type": c.strategy_type, "params": c.params} for c in configs]


@router.post("/")
def create_config(req: CreateStrategyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyService(db)
    config = svc.create_config(user.id, req.name, req.strategy_type, req.params)
    return {"id": config.id, "name": config.name}


@router.delete("/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = StrategyService(db)
    if svc.delete_config(config_id, user.id):
        return {"status": "deleted"}
    return {"error": "not found"}


@router.post("/{strategy_type}/signals")
def generate_signals(strategy_type: str, req: GenerateSignalsRequest):
    svc = StrategyService(None)
    return svc.generate_signals(strategy_type, req.params, req.symbols, req.start, req.end)
