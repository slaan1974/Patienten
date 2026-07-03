import json
from fastapi import WebSocket
from jose import JWTError

from services.auth_service import decode_token


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if hasattr(self, '_on_user_gone'):
                    await self._on_user_gone(user_id)

    @property
    def on_user_gone(self):
        return getattr(self, '_on_user_gone', None)

    @on_user_gone.setter
    def on_user_gone(self, callback):
        self._on_user_gone = callback

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: dict, exclude_user_id: int | None = None):
        for uid, connections in self.active_connections.items():
            if uid == exclude_user_id:
                continue
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def notify_lock_changed(self, table_name: str, record_id: int, locked_by: int | None, locked_by_name: str | None = None, exclude_user_id: int | None = None):
        msg = {
            "type": "lock_changed",
            "table_name": table_name,
            "record_id": record_id,
            "locked_by": locked_by,
            "locked_by_name": locked_by_name,
        }
        await self.broadcast(msg, exclude_user_id=exclude_user_id)


manager = ConnectionManager()
