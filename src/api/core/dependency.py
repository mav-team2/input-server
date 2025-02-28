from contextvars import ContextVar
from typing import Optional, Final, Annotated, Union

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker
from sqlalchemy.orm import Session

from src.api.database.core import engine

REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()

async def get_db() -> AsyncSession:
    session = async_scoped_session(async_sessionmaker(bind=engine), scopefunc=get_request_id)
    # log.debug("current session: %s", session)
    try:
        yield session
    finally:
        await session.remove()


DbSession = Annotated[Union[Session, AsyncSession], Depends(get_db)]
RequestId = Annotated[Optional[str], Depends(get_request_id)]