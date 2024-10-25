from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.api.database.core import Base
from src.api.models import TimeStampMixin, MyBaseModel


class AssistantId(Base, TimeStampMixin):
    __tablename__ = "assistant_id"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assistant_id : Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Assistant ID for chatGPT api")
    description : Mapped[str] = mapped_column(String(500), nullable=True)

    # presets = relationship("Preset", back_populates="assistant_id")


class AssistantIdBase(MyBaseModel):
    assistant_id: str
    description: Optional[str] = None


class AssistantIdCreate(AssistantIdBase):
    pass


class AssistantIdRead(AssistantIdBase):
    id : int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# class ThreadId(Base, TimeStampMixin):
#     __tablename__ = "thread_id"
#
#     id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     thread_id : Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="Thread ID for chatGPT api")
#     description : Mapped[str] = mapped_column(String(500), nullable=True)
#
#     presets = relationship("Preset", back_populates="thread_id")
#
#
# class ThreadIdBase(MyBaseModel):
#     thread_id: int
#     description: Optional[str] = None
#
# class ThreadIdCreate(ThreadIdBase):
#     pass
#
# class ThreadIdRead(ThreadIdBase):
#     id : int
#     created_at: Optional[datetime]
#     updated_at: Optional[datetime]