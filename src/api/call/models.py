from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.api.database.core import Base
from src.api.models import MyBaseModel, TimeStampMixin
from src.api.presets.models import PresetBase


class Call(Base, TimeStampMixin):
    __tablename__ = "call"

    id = Column(Integer, primary_key=True, index=True)
    # uuid = Column(String(36), nullable=False, unique=True, index=True, comment="UUID")
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_prompt = Column(String(1000), nullable=False, comment="입력 프롬프트")
    preset_id = Column(Integer, ForeignKey("presets.id"), nullable=False)
    prompt = Column(String(1000), nullable=False, comment="생성 프롬프트")

    # History와 User, Preset의 관계 설정
    # user = relationship("User", back_populates="call")
    preset = relationship("Preset", back_populates="calls")
    # result = relationship("Result", back_populates="call")


class CallBase(MyBaseModel):
    # user_id: int
    pass


class CallCreate(CallBase):
    input_prompt: str
    preset_id: Optional[int] = None
    prompt : str


class CallRead(CallBase):
    id: Optional[str]
    preset_id: int
    preset: Optional[PresetBase] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class CallRequset(MyBaseModel):
    input_prompt: str
    preset_id: int