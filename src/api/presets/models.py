import enum
from datetime import datetime
from typing import Optional, Any, Dict

from pydantic import Json
from sqlalchemy import Column, String, Integer, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.api.database.core import Base
from src.api.models import MyBaseModel, TimeStampMixin
from src.api.prompt.models import AssistantIdRead


# Enum 정의
class APIType(str, enum.Enum):
    T2I = "T2I"
    I2I = "I2I"


# SQLAlchemy 모델
class Preset(Base, TimeStampMixin):
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, index=True)
    parameter = Column(JSON, nullable=False)
    description = Column(String(200), nullable=True)
    api_type = Column(Enum(APIType), nullable=False, default=APIType.I2I)
    assistant_id_id: Mapped[int] = mapped_column(ForeignKey("assistant_id.id"), nullable=True,
                                                 comment="Assistant ID for chatGPT api")
    # thread_id_id: Mapped[int] = mapped_column(ForeignKey("thread_id.id"), nullable=True, comment="Thread ID for chatGPT api")

    calls = relationship("Call", back_populates="preset")
    assistant_id = relationship("AssistantId", back_populates="presets", lazy="joined")
    # thread_id = relationship("ThreadId", back_populates="preset")


class PresetBase(MyBaseModel):
    parameter: Dict[str, Any]
    description: Optional[str] = None
    api_type: APIType
    assistant_id_id: Optional[int] = None
    # thread_id_id : Optional[int] = None


class PresetCreate(PresetBase):
    pass


class PresetUpdate(PresetBase):
    pass

class PresetRead(PresetBase):
    id: Optional[int]
    assistant_id: Optional[AssistantIdRead] = None
    # thread_id : Optional[ThreadIdRead] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
