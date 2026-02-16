from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

trade_connections: list[WebSocket] = []


@router.websocket("/ws/trades")
async def trades_ws(websocket: WebSocket):
    await websocket.accept()
    trade_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        trade_connections.remove(websocket)
