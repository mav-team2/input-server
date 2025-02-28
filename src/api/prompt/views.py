# python
from fastapi import APIRouter, HTTPException, status
from typing import List
from sqlalchemy import select

from src.api.core.dependency import DbSession
from src.api.prompt.models import Assistant, AssistantCreate, AssistantRead
from src.api.prompt.services import get_assistant_id, create_assistant_id, delete_assistant_id

router = APIRouter()


@router.get("/", response_model=List[AssistantRead])
async def read_assistants(db_session: DbSession):
    """모든 어시스턴트 목록 조회."""
    result = await db_session.execute(select(Assistant))
    assistants = result.scalars().all()
    return assistants


@router.get("/{assistant_id}", response_model=AssistantRead)
async def read_assistant(assistant_id: int, db_session: DbSession):
    """어시스턴트 ID로 상세 조회."""
    assistant = await get_assistant_id(db_session, assistant_id)
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    return assistant


@router.post("/", response_model=AssistantRead, status_code=status.HTTP_201_CREATED)
async def create_assistant(assistant_in: AssistantCreate, db_session: DbSession):
    """새로운 어시스턴트 생성."""
    assistant = await create_assistant_id(db_session, assistant_in)
    if not assistant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create assistant")
    return assistant


@router.put("/{assistant_id}", response_model=AssistantRead)
async def update_assistant(assistant_id: int, assistant_in: AssistantCreate, db_session: DbSession):
    """어시스턴트 수정."""
    assistant = await get_assistant_id(db_session, assistant_id)
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")

    assistant.assistant_id = assistant_in.assistant_id
    assistant.description = assistant_in.description
    await db_session.commit()
    await db_session.refresh(assistant)
    return assistant


@router.delete("/{assistant_id}")
async def delete_assistant(assistant_id: int, db_session: DbSession):
    """어시스턴트 삭제."""
    assistant = await get_assistant_id(db_session, assistant_id)
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    await delete_assistant_id(db_session, assistant_id)
    return {"detail": "Assistant deleted"}