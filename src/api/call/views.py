import logging

from fastapi import APIRouter, HTTPException
from starlette import status

from src.api.core.dependency import DbSession

from src.api.call.models import CallRead, CallCreate, CallRequset
from .services import get, create
from src.api.preset.services import get as get_preset
from ..core import config
from src.api.prompt.chatGPT.chatGPTGenerator import OpenAIHandlerDependency
from src.api.prompt.services import create_prompt

# from ..queue.connection import rabbitMQClient

router = APIRouter()
logic_router = APIRouter()

log = logging.getLogger(__name__)


# @router.get("/", response_model=List[CallRead])
# def get_calls(common : CommonParameters):
#     """Get all entitys, or only those matching a given search term."""
#     return search_filter_sort_paginate(model="Entity", **common)


@router.get("/{call_id}", response_model=CallRead)
async def get_call(db_session: DbSession, call_id: int):
    call_ = await get(db_session=db_session, call_id=call_id)
    if not call_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Call not found"})

    return call_


@logic_router.post("/call", response_model=CallRead)
async def _call(db_session: DbSession, openai_handler: OpenAIHandlerDependency, call_in: CallRequset):
    try:
        #get preset
        preset = await get_preset(db_session=db_session, preset_id=call_in.preset_id)

        # get prompt
        prompt = await create_prompt(call_in.input_prompt, preset.assistant_id.assistant_id, openai_handler)

        # create call
        call_create: CallCreate = CallCreate(
            preset_id=preset.id,
            input_prompt=call_in.input_prompt,
            prompt=prompt
        )

        call = await create(db_session=db_session, call_in=call_create)
        data = CallRead.model_validate(call)

        # add to queue
        await rabbitMQClient.publish_message(config.RABBITMQ_ROUTING_KEY, data.model_dump_json(exclude=["created_at", "updated_at"]))

        return call
    except Exception as e:
        log.error("Error creating call: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": "Internal Server Error", "error": str(e)})
