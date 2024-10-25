import json
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from src.api.database.core import DbSession
# from src.api.database.services import CommonParameters, search_filter_sort_paginate
from src.api.presets.models import PresetRead, PresetCreate, PresetUpdate
from src.api.presets.services import get, create, get_all, update, delete

router = APIRouter()

log = logging.getLogger(__name__)


@router.get("/", response_model=List[PresetRead])
async def get_presets(db_session: DbSession):
    """Get all presets."""
    return await get_all(db_session=db_session)


@router.get("/{preset_id}", response_model=PresetRead)
async def get_preset(db_session: DbSession, preset_id: int):
    preset = await get(db_session=db_session, preset_id=preset_id)
    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Preset not found"})

    return preset


@router.post("/")
async def create_preset(db_session: DbSession, preset_in: PresetCreate):
    preset = await create(db_session=db_session, preset_in=preset_in)
    return preset


@router.put("/{preset_id}")
async def update_preset(db_session: DbSession, preset_id : int, preset_in: PresetUpdate):
    preset = await get(db_session, preset_id)
    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Preset not found"})

    preset = await update(db_session=db_session, preset=preset, preset_in=preset_in)
    return preset


@router.delete("/{preset_id}")
async def delete_preset(db_session: DbSession, preset_id: int):
    preset = await get(db_session=db_session, preset_id=preset_id)
    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Preset not found"})

    await delete(db_session, preset)
    return {"msg": "Preset deleted"}

