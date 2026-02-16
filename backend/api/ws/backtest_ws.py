import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/backtest/{backtest_id}")
async def backtest_ws(websocket: WebSocket, backtest_id: int):
    await websocket.accept()
    try:
        await websocket.send_text(json.dumps({"backtest_id": backtest_id, "status": "connected"}))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
