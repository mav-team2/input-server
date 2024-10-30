import logging
from typing import Optional, Type, Sequence

from fastapi import HTTPException
from sqlalchemy import select, update as _update, delete as _delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.api.database.core import DbSession
from src.api.presets.models import Preset, PresetCreate, PresetUpdate

log = logging.getLogger(__name__)


async def get(db_session: AsyncSession, preset_id: int) -> Optional[Preset]:
    return await db_session.get(Preset, preset_id)
    # return (await db_session.execute(select(Preset).where(Preset.id == preset_id).options(selectinload(Preset.assistant_id)))).scalar()


async def get_all(db_session: DbSession) -> Sequence[Preset]:
    return (await db_session.execute(select(Preset))).scalars().all()


async def create(db_session: AsyncSession, preset_in: PresetCreate) -> Optional[Preset]:
    # log.info("create preset: %s", preset_in.model_dump())
    preset = Preset(**preset_in.model_dump())
    db_session.add(preset)
    await db_session.commit()
    await db_session.refresh(preset)
    return preset


async def update(db_session: DbSession, preset: Preset, preset_in: PresetUpdate) -> Preset:
    update_data = preset_in.model_dump(exclude_unset=True)
    try:
        await db_session.execute(_update(Preset).where(Preset.id == preset.id).values(update_data))
        await db_session.refresh(preset)
    except Exception as e:
        log.error("Error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    return preset


async def delete(db_session: AsyncSession, preset: Preset):
    # await db_session.execute(_delete(Preset).where(Preset.id == preset_id))
    await db_session.delete(preset)
    await db_session.commit()
