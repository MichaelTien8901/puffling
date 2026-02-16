import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected WebSocket clients for optimization progress
_optimize_clients: list[WebSocket] = []


async def broadcast_optimize_progress(data: dict):
    message = json.dumps(data)
    disconnected = []
    for ws in _optimize_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        _optimize_clients.remove(ws)


@router.websocket("/ws/optimize")
async def optimize_ws(websocket: WebSocket):
    await websocket.accept()
    _optimize_clients.append(websocket)
    try:
        await websocket.send_text(json.dumps({"status": "connected"}))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _optimize_clients:
            _optimize_clients.remove(websocket)
