from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.broker_service import BrokerService

router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str
    side: str
    qty: float
    order_type: str = "market"


class ConfirmRequest(BaseModel):
    order_id: str


@router.get("/account")
def get_account(db: Session = Depends(get_db)):
    svc = BrokerService(db)
    return svc.get_account()


@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    svc = BrokerService(db)
    return svc.get_positions()


@router.post("/order")
def submit_order(req: OrderRequest, db: Session = Depends(get_db)):
    svc = BrokerService(db)
    return svc.submit_order(req.symbol, req.side, req.qty, req.order_type)


@router.post("/order/confirm")
def confirm_order(req: ConfirmRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = BrokerService(db)
    return svc.confirm_order(req.order_id, user.id)


@router.post("/order/cancel")
def cancel_order(req: ConfirmRequest, db: Session = Depends(get_db)):
    svc = BrokerService(db)
    return svc.cancel_order(req.order_id)
