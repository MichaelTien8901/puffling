from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.alert_service import alert_connections

router = APIRouter()


@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    alert_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        alert_connections.remove(websocket)
