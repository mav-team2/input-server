from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from src.api.preset.views import router as presets_router
from src.api.call.views import router as calls_router, logic_router as calls_logic_router
from src.api.ws.router import router as ws_router
from src.api.history.views import router as histories_router
from src.api.generation_setting.views import router as generation_settings_router
from src.api.prompt.views import router as prompts_router

class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}

api_router.include_router(ws_router, tags=["ws"])
api_router.include_router(calls_router, prefix="/call", tags=["calls"])
api_router.include_router(calls_logic_router, tags=["call"])
api_router.include_router(presets_router, prefix="/preset", tags=["preset"])
api_router.include_router(prompts_router, prefix="/prompt", tags=["prompt"])
api_router.include_router(histories_router, prefix="/history", tags=["history"])
api_router.include_router(generation_settings_router, prefix="/generation_setting", tags=["generation_setting"])