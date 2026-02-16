from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.backtest_service import BacktestService

router = APIRouter()


class BacktestRequest(BaseModel):
    strategy_type: str
    params: dict = {}
    symbols: list[str]
    start: str
    end: str
    strategy_id: int | None = None


@router.post("/")
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = BacktestService(db)
    return svc.run(user.id, req.strategy_type, req.params, req.symbols, req.start, req.end, req.strategy_id)


@router.get("/")
def list_results(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = BacktestService(db)
    results = svc.get_results(user.id)
    return [{"id": r.id, "metrics": r.metrics, "created_at": str(r.created_at)} for r in results]


@router.get("/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = BacktestService(db)
    result = svc.get_result(result_id, user.id)
    if result:
        return {"id": result.id, "metrics": result.metrics, "created_at": str(result.created_at)}
    return {"error": "not found"}
