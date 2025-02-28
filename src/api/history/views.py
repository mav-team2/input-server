# python
from fastapi import APIRouter, HTTPException, status
from typing import List

from src.api.database.core import DbSession
from src.api.history.models import HistoryRead, HistoryCreate, HistoryUpdate
from src.api.history.services import (
    get,
    get_all,
    get_by_generation_setting,
    create,
    update,
    delete,
)

router = APIRouter()


@router.get("/", response_model=List[HistoryRead])
async def read_histories(db_session: DbSession):
    """모든 히스토리 목록 조회."""
    histories = await get_all(db_session)
    return histories


@router.get("/{history_id}", response_model=HistoryRead)
async def read_history(history_id: int, db_session: DbSession):
    """히스토리 ID로 히스토리 상세 조회."""
    history = await get(db_session, history_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    return history


@router.get("/by_generation/{generation_setting_id}", response_model=List[HistoryRead])
async def read_history_by_generation(generation_setting_id: int, db_session: DbSession):
    """generation_setting ID에 해당하는 히스토리 목록 조회."""
    histories = await get_by_generation_setting(db_session, generation_setting_id)
    return histories


@router.post("/", response_model=HistoryRead, status_code=status.HTTP_201_CREATED)
async def create_history(history_in: HistoryCreate, db_session: DbSession):
    """새로운 히스토리 생성."""
    history = await create(db_session, history_in)
    return history


@router.put("/{history_id}", response_model=HistoryRead)
async def update_history(history_id: int, history_in: HistoryUpdate, db_session: DbSession):
    """히스토리 수정."""
    history = await get(db_session, history_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    history_updated = await update(db_session, history, history_in)
    return history_updated


@router.delete("/{history_id}")
async def delete_history(history_id: int, db_session: DbSession):
    """히스토리 삭제."""
    history = await get(db_session, history_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    await delete(db_session, history)
    return {"detail": "History deleted"}