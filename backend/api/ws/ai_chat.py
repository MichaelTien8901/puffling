import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/ai/chat")
async def ai_chat_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            message = data.get("message", "")
            # Stream response back
            await websocket.send_text(json.dumps({"type": "start"}))
            try:
                from puffin.ai import ClaudeProvider
                provider = ClaudeProvider()
                response = provider.generate(message)
                await websocket.send_text(json.dumps({"type": "token", "content": response}))
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
            await websocket.send_text(json.dumps({"type": "end"}))
    except WebSocketDisconnect:
        pass
