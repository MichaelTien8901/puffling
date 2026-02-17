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
        if settings.broker == "ibkr":
            from puffin.broker import IBKRBroker
            return IBKRBroker(
                host=settings.ibkr_host,
                port=settings.ibkr_port,
                client_id=settings.ibkr_client_id,
                paper=settings.paper_trading,
            )
        else:
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

    def submit_order(
        self, symbol: str, side: str, qty: float, order_type: str = "market",
        asset_type: str = "STK", exchange: str = "SMART", currency: str = "USD",
        expiry: str | None = None, strike: float | None = None,
        right: str | None = None, multiplier: str | None = None,
        pair_currency: str | None = None, limit_price: float | None = None,
        stop_price: float | None = None, time_in_force: str = "DAY",
    ) -> dict:
        order_id = str(uuid.uuid4())
        _pending_orders[order_id] = {
            "symbol": symbol, "side": side, "qty": qty, "order_type": order_type,
            "asset_type": asset_type, "exchange": exchange, "currency": currency,
            "expiry": expiry, "strike": strike, "right": right,
            "multiplier": multiplier, "pair_currency": pair_currency,
            "limit_price": limit_price, "stop_price": stop_price,
            "time_in_force": time_in_force,
        }
        # Build descriptive summary
        spec_parts = [f"{side} {qty} {symbol} ({order_type})"]
        if asset_type != "STK":
            spec_parts.append(f"type={asset_type}")
        if expiry:
            spec_parts.append(f"exp={expiry}")
        if strike is not None:
            spec_parts.append(f"strike={strike}")
        if right:
            spec_parts.append(f"right={right}")
        if pair_currency:
            spec_parts.append(f"pair={pair_currency}")
        if exchange != "SMART":
            spec_parts.append(f"exch={exchange}")
        if currency != "USD":
            spec_parts.append(f"ccy={currency}")
        if limit_price is not None:
            spec_parts.append(f"limit={limit_price}")
        if stop_price is not None:
            spec_parts.append(f"stop={stop_price}")

        return {
            "order_id": order_id,
            "status": "pending_confirmation",
            "summary": " ".join(spec_parts),
        }

    def _needs_contract_spec(self, order: dict) -> bool:
        return (
            order.get("asset_type", "STK") != "STK"
            or order.get("exchange", "SMART") != "SMART"
            or order.get("currency", "USD") != "USD"
        )

    def confirm_order(self, order_id: str, user_id: str) -> dict:
        order = _pending_orders.pop(order_id, None)
        if not order:
            return {"error": "Order not found or already processed"}

        broker = self._get_broker()
        from puffin.broker import Order, OrderSide, OrderType, TimeInForce

        puffin_order = Order(
            symbol=order["symbol"],
            side=OrderSide(order["side"]),
            qty=order["qty"],
            type=OrderType(order["order_type"]),
            limit_price=order.get("limit_price"),
            stop_price=order.get("stop_price"),
            time_in_force=TimeInForce(order.get("time_in_force", "DAY").lower()),
        )

        if self._needs_contract_spec(order):
            from puffin.broker import ContractSpec
            spec = ContractSpec(
                asset_type=order.get("asset_type", "STK"),
                exchange=order.get("exchange", "SMART"),
                currency=order.get("currency", "USD"),
                expiry=order.get("expiry"),
                strike=order.get("strike"),
                right=order.get("right"),
                multiplier=order.get("multiplier"),
                pair_currency=order.get("pair_currency"),
            )
            result = broker.submit_order_with_spec(puffin_order, spec)
        else:
            result = broker.submit_order(
                symbol=order["symbol"],
                side=OrderSide(order["side"]),
                qty=order["qty"],
                order_type=OrderType(order["order_type"]),
            )

        trade = TradeHistory(
            user_id=user_id, symbol=order["symbol"], side=order["side"],
            qty=order["qty"], price=0.0,
            asset_type=order.get("asset_type", "STK"),
            exchange=order.get("exchange", "SMART"),
            currency=order.get("currency", "USD"),
            expiry=order.get("expiry"),
            strike=order.get("strike"),
            right=order.get("right"),
        )
        self.db.add(trade)
        self.db.commit()
        return {"order_id": order_id, "status": "submitted", "broker_order": str(result)}

    def cancel_order(self, order_id: str) -> dict:
        if _pending_orders.pop(order_id, None):
            return {"order_id": order_id, "status": "cancelled"}
        return {"error": "Order not found"}
