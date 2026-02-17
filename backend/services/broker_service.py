import json
import uuid

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.trade_history import TradeHistory

# Pending orders awaiting confirmation
_pending_orders: dict[str, dict] = {}


class BrokerService:
    def __init__(self, db: Session):
        self.db = db

    def _get_broker(self):
        from puffin.broker import AlpacaBroker
        return AlpacaBroker(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            paper=settings.paper_trading,
        )

    def get_account(self) -> dict:
        broker = self._get_broker()
        info = broker.get_account()
        return {"equity": info.equity, "cash": info.cash, "buying_power": info.buying_power}

    def get_positions(self) -> list[dict]:
        broker = self._get_broker()
        positions = broker.get_positions()
        return [
            {"symbol": p.symbol, "qty": p.qty, "avg_price": p.avg_entry_price, "current_price": p.current_price}
            for p in positions
        ]

    def submit_order(self, symbol: str, side: str, qty: float, order_type: str = "market") -> dict:
        order_id = str(uuid.uuid4())
        _pending_orders[order_id] = {
            "symbol": symbol, "side": side, "qty": qty, "order_type": order_type,
        }
        return {
            "order_id": order_id,
            "status": "pending_confirmation",
            "summary": f"{side} {qty} {symbol} ({order_type})",
        }

    def confirm_order(self, order_id: str, user_id: str) -> dict:
        order = _pending_orders.pop(order_id, None)
        if not order:
            return {"error": "Order not found or already processed"}
        broker = self._get_broker()
        from puffin.broker import OrderSide, OrderType
        result = broker.submit_order(
            symbol=order["symbol"],
            side=OrderSide(order["side"]),
            qty=order["qty"],
            order_type=OrderType(order["order_type"]),
        )
        trade = TradeHistory(
            user_id=user_id, symbol=order["symbol"], side=order["side"],
            qty=order["qty"], price=0.0,  # filled price from broker callback
        )
        self.db.add(trade)
        self.db.commit()
        return {"order_id": order_id, "status": "submitted", "broker_order": str(result)}

    def cancel_order(self, order_id: str) -> dict:
        if _pending_orders.pop(order_id, None):
            return {"order_id": order_id, "status": "cancelled"}
        return {"error": "Order not found"}
