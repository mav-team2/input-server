from fastapi import FastAPI, status

import logging

from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from src.api.router import api_router
from src.api.core.log import configure_logging

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


app = FastAPI(
    title="Input API for Diffusion Image Models",
    description="This API is used to send images to the Diffusion Image Models.",
    openapi_url="/docs/openapi.json",
    redoc_url="/redoc",
    exception_handlers={404: not_found}
)


app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(api_router, prefix="/api")

