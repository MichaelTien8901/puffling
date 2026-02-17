import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_price_clients: list[WebSocket] = []
_subscriptions: dict[int, set[str]] = {}
_poll_task: asyncio.Task | None = None
_executor = ThreadPoolExecutor(max_workers=2)


def _fetch_prices(symbols: list[str]) -> dict[str, float]:
    """Fetch last prices via yfinance (runs in thread)."""
    import yfinance as yf

    results = {}
    for sym in symbols:
        try:
            info = yf.Ticker(sym).fast_info
            results[sym] = float(info["last_price"])
        except Exception:
            pass
    return results


async def _poll_prices():
    """Background loop: fetch prices for all subscribed symbols every 10s."""
    loop = asyncio.get_event_loop()
    while _price_clients:
        all_symbols: set[str] = set()
        for subs in _subscriptions.values():
            all_symbols.update(subs)
        if all_symbols:
            try:
                prices = await loop.run_in_executor(
                    _executor, _fetch_prices, list(all_symbols)
                )
                ts = time.time()
                for sym, price in prices.items():
                    await broadcast_price(sym, price, ts)
            except Exception:
                pass
        await asyncio.sleep(10)


async def broadcast_price(symbol: str, price: float, timestamp: float):
    message = json.dumps(
        {"symbol": symbol, "price": price, "timestamp": timestamp}
    )
    disconnected = []
    for ws in _price_clients:
        ws_id = id(ws)
        if ws_id in _subscriptions and symbol in _subscriptions[ws_id]:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
    for ws in disconnected:
        _price_clients.remove(ws)
        _subscriptions.pop(id(ws), None)


@router.websocket("/ws/prices")
async def prices_ws(websocket: WebSocket):
    global _poll_task
    await websocket.accept()
    _price_clients.append(websocket)
    _subscriptions[id(websocket)] = set()

    # Start poll task if this is the first client
    if _poll_task is None or _poll_task.done():
        _poll_task = asyncio.create_task(_poll_prices())

    try:
        await websocket.send_text(json.dumps({"status": "connected"}))
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action = data.get("action")
            symbol = data.get("symbol", "").upper()
            if action == "subscribe" and symbol:
                _subscriptions[id(websocket)].add(symbol)
            elif action == "unsubscribe" and symbol:
                _subscriptions[id(websocket)].discard(symbol)
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _price_clients:
            _price_clients.remove(websocket)
        _subscriptions.pop(id(websocket), None)
