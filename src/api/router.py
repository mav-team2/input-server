from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from src.api.call.views import router as call_route
from src.api.presets.views import router as preset_route


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


api_router.include_router(call_route, prefix="/call", tags=["call"])
api_router.include_router(preset_route, prefix="/presets", tags=["presets"])