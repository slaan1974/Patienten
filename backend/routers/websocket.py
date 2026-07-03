from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, async_session_factory
from services.auth_service import decode_token, get_current_user
from websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if payload is None:
        await websocket.close(code=4001)
        return
    user_id = int(payload["sub"])
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "heartbeat":
                await manager.send_to_user(user_id, {"type": "heartbeat_ack"})
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception:
        await manager.disconnect(websocket, user_id)
