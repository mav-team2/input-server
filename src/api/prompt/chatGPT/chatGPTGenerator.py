import logging
import os
import asyncio
from typing import Optional, List, Any, Annotated

import openai
from fastapi import Depends
from openai.types.beta.threads import Run
from openai.types.beta.thread_create_params import Message

from src.api import config

log = logging.getLogger(__name__)

"""Construct a new async openai client instance.

This automatically infers the following arguments from their corresponding environment variables if they are not provided:
- `api_key` from `OPENAI_API_KEY`
- `organization` from `OPENAI_ORG_ID`
- `project` from `OPENAI_PROJECT_ID`
"""


class ChatGPTHandler:
    def __init__(self, api_key: str):
        self.client = openai.AsyncClient(api_key=api_key)

    async def get_or_create_assistant(self, assistant_id):
        assistant = await self.retrieve_assistant(assistant_id)
        if assistant is None:
            assistant = self.create_assistant(assistant_id)

        return assistant

    async def retrieve_assistant(self, assistant_id: str):
        return self.client.beta.assistants.retrieve(assistant_id)

    async def retrieve_thread(self, thread_id: str):
        return self.client.beta.threads.retrieve(thread_id)

    async def create_thread(self):
        return self.client.beta.threads.create()

    async def create_thread_with_messages(self, prompt: str):
        message = {
            "role": "user",
            "content": prompt
        }

        return self.client.beta.threads.create(messages=[message])

    async def remove_thread(self, thread_id: str):
        return self.client.beta.threads.delete(thread_id)

    async def create_message(self, prompt: str, thread_id: Optional[str] = None):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

    async def list_messages(self, thread_id: str):
        return self.client.beta.threads.messages.list(thread_id=thread_id)

    async def create_run(self, thread_id: str, assistant_id: str, **kwargs):
        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            **kwargs
        )

    async def retrieve_run(self, thread_id: str, run_id: str) -> Run:
        return await self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    async def retrieve_run_when_done(self, thread_id: str, run_id: str):
        while True:
            run = await self.retrieve_run(thread_id, run_id)
            if run.status in ['completed', 'failed']:
                return run

            await asyncio.sleep(1)

    async def handle_run_completion(self, thread_id: str, run_id: str, interval=1.0):
        while True:
            try:
                run = await self.retrieve_run(thread_id, run_id)

                if run.status in ['completed', 'failed']:
                    return run

                if run.status in ['cancelled', 'expired']:
                    raise Exception(f"Run status: {run.status}")

            except Exception as e:
                # 오류 발생 시 로그를 남기거나 추가적인 처리 가능
                print(f"Error retrieving run status: {e}")
                raise

            # interval 시간만큼 대기 후 다시 상태 체크
            await asyncio.sleep(interval)


async def get_openai_handler() -> ChatGPTHandler:
    api_key = config.OPENAI_API_KEY

    log.info("Using Asynchronous Mode")
    return ChatGPTHandler(api_key=api_key)


OpenAIHandlerDependency = Annotated[ChatGPTHandler, Depends(get_openai_handler)]
