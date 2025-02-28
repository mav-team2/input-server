import asyncio
import logging

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.api.database.core import DbSession
from src.api.ws.handler import handle_message

router = APIRouter()

log = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: DbSession):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            log.info(f"data: {data}")
            await handle_message(websocket, data, db)
    except (WebSocketDisconnect, asyncio.CancelledError):
        await websocket.close()
