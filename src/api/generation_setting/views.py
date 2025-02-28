# python
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.api.database.core import DbSession
from src.api.generation_setting.models import (
    GenerationSettingCreate,
    GenerationSettingUpdate,
    GenerationSettingRead,
    GenerationSettingDetail,
)
from src.api.generation_setting.services import (
    get,
    get_all,
    create,
    update,
    delete
)

router = APIRouter()

@router.get("/", response_model=List[GenerationSettingRead])
async def read_generation_settings(db_session: DbSession):
    """모든 생성 설정 목록 조회."""
    settings = await get_all(db_session)
    return settings

@router.get("/{generation_setting_id}", response_model=GenerationSettingDetail)
async def read_generation_setting(generation_setting_id: int, db_session: DbSession):
    """생성 설정 ID로 상세 조회."""
    setting = await get(db_session, generation_setting_id)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation setting not found")
    return setting

@router.post("/", response_model=GenerationSettingRead, status_code=status.HTTP_201_CREATED)
async def create_generation_setting(setting_in: GenerationSettingCreate, db_session: DbSession):
    """새로운 생성 설정 생성."""
    setting = await create(db_session, setting_in)
    if not setting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create generation setting")
    return setting

@router.put("/{generation_setting_id}", response_model=GenerationSettingRead)
async def update_generation_setting(generation_setting_id: int, setting_in: GenerationSettingUpdate, db_session: DbSession):
    """생성 설정 수정."""
    setting = await get(db_session, generation_setting_id)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation setting not found")
    setting = await update(db_session, setting, setting_in)
    return setting

@router.delete("/{generation_setting_id}")
async def delete_generation_setting(generation_setting_id: int, db_session: DbSession):
    """생성 설정 삭제."""
    setting = await get(db_session, generation_setting_id)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation setting not found")
    await delete(db_session, setting)
    return {"detail": "Generation setting deleted"}