from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Final, Optional, Union, Any
from fastapi import FastAPI, status

import os
import logging

from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.routing import compile_path

from src.api.router import api_router
from .log import configure_logging
from .queue.rabbitmq_client import rabbitMQClient

log = logging.getLogger(__name__)

# we configure the logging level and format
configure_logging()
log.warn("current log level: %s", logging.getLogger().getEffectiveLevel())

"""
로컬 서버에서 최대한 많은 기능을 덜어낸다.
api server에선 콜 기록만 저장
프롬프트와 call uuid, api type을 통째로 queue에 전송
gpt api는 워커로 빼두기
"""

"""
app
 - api
    - auth
    - prompts
    - preset(admin)
    - history(admin)
    - queueManger(admnin)
 - front
"""


async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": [{"msg": "Not Found."}]}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.debug("Starting rabbitmq connection")
    try:
        await rabbitMQClient.start()
        yield

    except BaseException as e:
        log.error("Error connecting rabbitmq: %s", e)

    finally:
        if rabbitMQClient.is_connected:
            await rabbitMQClient.stop()


app = FastAPI(
    title="Input API for Diffusion Image Models",
    description="This API is used to send images to the Diffusion Image Models.",
    openapi_url="/docs/openapi.json",
    redoc_url="/redoc",
    exception_handlers={404: not_found},
    lifespan=lifespan
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


def get_path_params_from_request(request: Request) -> Union[dict[Any, Any], dict[str, Union[str, Any]]]:
    path_params = {}
    for r in api_router.routes:
        path_regex, path_format, param_converters = compile_path(r.path)
        path = request["path"].removeprefix("/api/v1")  # remove the /api/v1 for matching
        match = path_regex.match(path)
        if match:
            path_params = match.groupdict()
    return path_params


REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


app.include_router(api_router, prefix="/api")

