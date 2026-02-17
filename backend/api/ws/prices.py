import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.config import settings

router = APIRouter()

_logger = logging.getLogger(__name__)

_price_clients: list[WebSocket] = []
_subscriptions: dict[int, set[str]] = {}
_poll_task: asyncio.Task | None = None
_executor = ThreadPoolExecutor(max_workers=2)

_ib_client = None


def _fetch_yfinance(symbols: list[str]) -> dict[str, float]:
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


def _fetch_alpaca(symbols: list[str]) -> dict[str, float]:
    """Fetch last prices via Alpaca market data API."""
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestTradeRequest

    client = StockHistoricalDataClient(
        settings.alpaca_api_key, settings.alpaca_secret_key
    )
    trades = client.get_stock_latest_trade(
        StockLatestTradeRequest(symbol_or_symbols=symbols)
    )
    return {sym: float(trade.price) for sym, trade in trades.items()}


def _fetch_ibkr(symbols: list[str]) -> dict[str, float]:
    """Fetch last prices via IB Gateway / TWS."""
    from ib_insync import IB, Stock

    global _ib_client
    if _ib_client is None or not _ib_client.isConnected():
        _ib_client = IB()
        _ib_client.connect(
            settings.ibkr_host, settings.ibkr_port, clientId=settings.ibkr_client_id
        )

    contracts = [Stock(sym, "SMART", "USD") for sym in symbols]
    _ib_client.qualifyContracts(*contracts)
    tickers = _ib_client.reqTickers(*contracts)
    results = {}
    for ticker in tickers:
        sym = ticker.contract.symbol
        price = ticker.marketPrice()
        if price == price:  # not NaN
            results[sym] = float(price)
    return results


def _resolve_fetcher():
    """Pick the best available price provider."""
    if settings.alpaca_api_key and settings.alpaca_secret_key:
        _logger.info("Price provider: Alpaca")
        return _fetch_alpaca
    if settings.broker == "ibkr":
        _logger.info("Price provider: IBKR")
        return _fetch_ibkr
    _logger.info("Price provider: yfinance")
    return _fetch_yfinance


async def _poll_prices():
    """Background loop: fetch prices for all subscribed symbols every 10s."""
    loop = asyncio.get_event_loop()
    fetcher = _resolve_fetcher()
    while _price_clients:
        all_symbols: set[str] = set()
        for subs in _subscriptions.values():
            all_symbols.update(subs)
        if all_symbols:
            sym_list = list(all_symbols)
            try:
                prices = await loop.run_in_executor(
                    _executor, fetcher, sym_list
                )
            except Exception:
                _logger.warning(
                    "Primary provider failed, falling back to yfinance",
                    exc_info=True,
                )
                try:
                    prices = await loop.run_in_executor(
                        _executor, _fetch_yfinance, sym_list
                    )
                except Exception:
                    prices = {}
            ts = time.time()
            for sym, price in prices.items():
                await broadcast_price(sym, price, ts)
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
