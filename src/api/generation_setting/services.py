import logging
from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import select, update as _update
from sqlalchemy.orm import selectinload
from starlette import status

from src.api.core.dependency import DbSession
from src.api.generation_setting.models import GenerationSetting, GenerationSettingCreate, GenerationSettingUpdate

log = logging.getLogger(__name__)


async def get(db_session: DbSession, generation_setting_id: int) -> Optional[GenerationSetting]:
    return (await db_session.execute(
        select(GenerationSetting)
        .where(GenerationSetting.id == generation_setting_id)
        .options(selectinload(GenerationSetting.preset_id), selectinload(GenerationSetting.assistant_id))
    )).scalar()


async def get_all(db_session: DbSession) -> Sequence[GenerationSetting]:
    return (await db_session.execute(select(GenerationSetting))).scalars().all()

# async def get_valid_setting(db_session: DbSession) -> Optional[GenerationSetting]:


async def create(
    db_session: DbSession,
    setting_in: GenerationSettingCreate
) -> Optional[GenerationSetting]:
    setting = GenerationSetting(**setting_in.model_dump())
    db_session.add(setting)
    await db_session.commit()
    await db_session.refresh(setting)
    return setting


async def update(
    db_session: DbSession,
    setting: GenerationSetting,
    setting_in: GenerationSettingUpdate
) -> GenerationSetting:
    update_data = setting_in.model_dump(exclude_unset=True)
    try:
        await db_session.execute(
            _update(GenerationSetting)
            .where(GenerationSetting.id == setting.id)
            .values(update_data)
        )
        await db_session.refresh(setting)
        return setting

    except Exception as e:
        log.error("Error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


async def delete(db_session: DbSession, setting: GenerationSetting):
    await db_session.delete(setting)
    await db_session.commit()
