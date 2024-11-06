import logging
from typing import Optional

from .chatGPT.chatGPTGenerator import ChatGPTHandler
from .models import AssistantId, AssistantIdCreate
from ..database.core import DbSession

log = logging.getLogger(__name__)


class OPENAIError(Exception):
    def __init__(self, message):
        self.message = f"open ai error : {message}"
        super().__init__(message)


async def create_prompt(prompt: str, assistant_id: str, handler: ChatGPTHandler):
    try:
        assistant = await handler.retrieve_assistant(assistant_id)
        if assistant is None:
            raise Exception("Assistant not found")

        # thread = chatGPT_generator.retrieve_thread(thread_id)
        thread = await handler.create_thread()
        messages = await handler.create_message(prompt, thread.id)
        run = await handler.create_run(thread.id, assistant_id)
        await handler.handle_run_completion(thread.id, run.id)
        messages = await handler.list_messages(thread.id)

        response = messages.data[0].content[0].text.value
        return response
    except Exception as e:
        log.error(f"OPENAI Error: {e}")
        raise OPENAIError(e)
    finally:
        await handler.remove_thread(thread.id)
        log.info("Thread removed")


# CRUD assistant_id
async def get_assistant_id(db_session: DbSession, assistant_id: int) -> Optional[AssistantId]:
    # return db_session.query(AssistantId).get(assistant_id)
    return await db_session.get(AssistantId, assistant_id)


async def create_assistant_id(db_session: DbSession, assistant_id_in: AssistantIdCreate) -> AssistantId:
    assistant_id = AssistantId(**assistant_id_in.model_dump())
    db_session.add(assistant_id)
    await db_session.commit()
    await db_session.refresh(assistant_id)
    return assistant_id


async def delete_assistant_id(db_session: DbSession, assistant_id_id: int):
    assistant_id = await db_session.get(AssistantId, assistant_id_id)
    await db_session.delete(assistant_id)
    await db_session.commit()