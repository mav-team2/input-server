from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from presets.views import router as presets_router
from call.views import router as calls_router


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


api_router.include_router(calls_router, prefix="/call", tags=["call"])

api_router.include_router(presets_router, prefix="/presets", tags=["presets"])


