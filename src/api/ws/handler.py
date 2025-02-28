import asyncio
import json
import logging

from fastapi import WebSocket
from pydantic import ValidationError

from src.api.database.core import DbSession
from src.api.generation_setting.tasks import generate_image_task
from src.api.ws.schemas import WebSocketMessage, GeneratePayload

logger = logging.getLogger(__name__)

async def handle_message(websocket: WebSocket, data: str, db: DbSession):
    try:
        message_dict = json.loads(data)  # JSON 데이터 파싱
        message = WebSocketMessage(**message_dict)  # 기본 검증

        logger.info(f"data: {data}")

        if message.action == "generate":
            payload = GeneratePayload(**message.payload)
            asyncio.create_task(generate_image_task(payload.input_text, payload.setting_id, db, websocket))

    except ValidationError as e:
        await websocket.send_text(json.dumps({"error": "Invalid message format", "details": e.errors()}))

    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
