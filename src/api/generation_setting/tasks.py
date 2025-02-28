import asyncio

from src.api.core.config import config
from src.api.core.dependency import DbSession
from src.api.generation_setting.services import get as generation_get
from src.api.history.models import History, HistoryCreate
from src.api.history.services import create as history_create
from src.api.prompt.chatGPT.chatGPTGenerator import ChatGPTHandler
from src.api.ws.ws_manager import ws_manager



async def generate_image_task(input_text : str, setting_id: int, request_id: str, db: DbSession):
    # ws = await ws_manager.get(request_id)
    setting = await generation_get(db, setting_id)
    if not setting:
        await ws_manager.send_message(request_id, {"error": "Generation setting not found"})
        return

    # call prompt
    gpt_client = ChatGPTHandler(config.OPENAI_API_KEY)
    await ws_manager.send_message(request_id, {"step" : "gpt_call"})
    prompt = await gpt_client.call(input_text, setting.assistant.assistant_id)
    await ws_manager.send_message(request_id, {"step" : "gpt_call", "prompt" : prompt})

    # call stable diffusion
    await ws_manager.send_message(request_id, {"step" : "sd_call", "progress" : 0})
    # sleep 3 sec
    await asyncio.sleep(3)
    await ws_manager.send_message(request_id, {"step" : "sd_call", "progress" : 100})

    history = HistoryCreate(
        prompt=prompt,
        generation_setting_id=setting.id
    )
    await history_create(db, history)

