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

