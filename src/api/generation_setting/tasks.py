import asyncio
import json
import logging

from fastapi import WebSocket

from src.api.core.config import config
from src.api.database.core import DbSession
from src.api.generation_setting.services import get as generation_get
from src.api.history.models import HistoryCreate
from src.api.history.services import create as history_create
from src.api.prompt.chatGPT.chatGPTGenerator import ChatGPTHandler

logger = logging.getLogger(__name__)

async def generate_image_task(input_text : str, setting_id: int, db: DbSession, websocket: WebSocket):
    logger.info(f"Generating image for {input_text}")

    setting = await generation_get(db, setting_id)
    if not setting:
        await websocket.send_text(json.dumps({"error": "Generation setting not found"}))
        return

    # call prompt
    # gpt_client = ChatGPTHandler(config.OPENAI_API_KEY)
    # await ws_manager.send_message(request_id, {"step" : "gpt_call"})
    # prompt = await gpt_client.call(input_text, setting.assistant.assistant_id)
    # await ws_manager.send_message(request_id, {"step" : "gpt_call", "prompt" : prompt})

    # call stable diffusion
    await websocket.send_text(json.dumps({"step" : "sd_call", "progress" : 1}))
    # sleep 3 sec
    await asyncio.sleep(3)
    await websocket.send_text(json.dumps({"step" : "sd_call", "progress" : 100}))

    history = HistoryCreate(
        prompt="prompt",
        generation_setting_id=setting.id
    )
    await history_create(db, history)

