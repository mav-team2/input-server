import logging
from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import select, update as _update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.api.database.core import DbSession
from src.api.history.models import History, HistoryCreate, HistoryUpdate

log = logging.getLogger(__name__)


async def get(db_session: AsyncSession, history_id: int) -> Optional[History]:
    return (await db_session.execute(
        select(History)
        .where(History.id == history_id)
        .options(selectinload(History.generation_setting))
    )).scalar()


async def get_all(db_session: DbSession) -> Sequence[History]:
    return (await db_session.execute(select(History))).scalars().all()


async def get_by_generation_setting(
    db_session: AsyncSession,
    generation_setting_id: int
) -> Sequence[History]:
    return (await db_session.execute(
        select(History)
        .where(History.generation_setting_id == generation_setting_id)
    )).scalars().all()


async def create(
    db_session: AsyncSession,
    history_in: HistoryCreate
) -> History:
    history = History(**history_in.model_dump())
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)
    return history


async def update(
    db_session: DbSession,
    history: History,
    history_in: HistoryUpdate
) -> History:
    update_data = history_in.model_dump(exclude_unset=True)
    try:
        await db_session.execute(
            _update(History)
            .where(History.id == history.id)
            .values(update_data)
        )
        await db_session.refresh(history)
    except Exception as e:
        log.error("Error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return history


async def delete(db_session: AsyncSession, history: History):
    await db_session.delete(history)
    await db_session.commit()