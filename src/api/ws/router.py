import asyncio
import logging

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.api.core.dependency import RequestId
from src.api.ws.ws_manager import ws_manager

router = APIRouter()

log = logging.getLogger(__name__)

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, request_id: RequestId):
    # 요청 스코프에 request_id를 설정 (추후 미들웨어 등에서 활용 가능)
    await ws_manager.connect(request_id, websocket)
    try:
        await asyncio.Future()
    except (WebSocketDisconnect, asyncio.CancelledError):
        ws_manager.disconnect(request_id)