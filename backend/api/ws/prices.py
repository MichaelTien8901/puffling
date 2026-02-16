import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/prices")
async def prices_ws(websocket: WebSocket):
    await websocket.accept()
    subscribed_symbols: set[str] = set()
    try:
        while True:
            msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            data = json.loads(msg)
            if data.get("action") == "subscribe":
                subscribed_symbols.add(data["symbol"])
            elif data.get("action") == "unsubscribe":
                subscribed_symbols.discard(data["symbol"])
    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        return
