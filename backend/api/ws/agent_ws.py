from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.autonomous_agent_service import agent_connections

router = APIRouter()


@router.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket):
    await websocket.accept()
    agent_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        agent_connections.remove(websocket)
