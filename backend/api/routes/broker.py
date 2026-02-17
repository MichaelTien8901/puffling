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
    # Contract spec fields for options, futures, forex, non-US stocks
    asset_type: str = "STK"
    exchange: str = "SMART"
    currency: str = "USD"
    expiry: str | None = None
    strike: float | None = None
    right: str | None = None
    multiplier: str | None = None
    pair_currency: str | None = None
    # Advanced order fields
    limit_price: float | None = None
    stop_price: float | None = None
    time_in_force: str = "DAY"


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
    return svc.submit_order(
        symbol=req.symbol, side=req.side, qty=req.qty, order_type=req.order_type,
        asset_type=req.asset_type, exchange=req.exchange, currency=req.currency,
        expiry=req.expiry, strike=req.strike, right=req.right,
        multiplier=req.multiplier, pair_currency=req.pair_currency,
        limit_price=req.limit_price, stop_price=req.stop_price,
        time_in_force=req.time_in_force,
    )


@router.post("/order/confirm")
def confirm_order(req: ConfirmRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc = BrokerService(db)
    return svc.confirm_order(req.order_id, user.id)


@router.post("/order/cancel")
def cancel_order(req: ConfirmRequest, db: Session = Depends(get_db)):
    svc = BrokerService(db)
    return svc.cancel_order(req.order_id)
