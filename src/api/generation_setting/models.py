from datetime import datetime
from croniter import croniter
from typing import Optional

from pydantic import field_validator
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.api.database.core import Base
from src.api.database.models import TimeStampMixin, MyBaseModel
from src.api.preset.models import PresetRead
from src.api.prompt.models import AssistantRead


class GenerationSetting(Base, TimeStampMixin):
    __tablename__ = "generation_settings"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    preset_id : Mapped[int] = mapped_column(ForeignKey("preset.id"), nullable=False, index=True)
    assistant_id : Mapped[int] = mapped_column(ForeignKey("assistant.id"), nullable=False, index=True)
    cron_rule : Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    next_run_time : Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    description : Mapped[str] = mapped_column(String(500), nullable=True)

    preset = relationship("Preset", back_populates="generation_settings")
    assistant = relationship("Assistant", back_populates="generation_settings")
    histories = relationship("History", back_populates="generation_setting")

class GenerationSettingBase(MyBaseModel):
    preset_id : int
    assistant_id : int
    cron_rule : str
    next_run_time : Optional[datetime] = None
    description : Optional[str] = None

    @field_validator('cron_rule')
    def validate_cron_expression(cls, v):
        try:
            if not croniter.is_valid(v):
                raise ValueError('유효하지 않은 cron 표현식입니다')
            return v
        except ValueError as e:
            raise ValueError(f'cron 표현식 오류: {str(e)}')

class GenerationSettingCreate(GenerationSettingBase):
    pass

class GenerationSettingUpdate(GenerationSettingBase):
    preset_id: Optional[int] = None
    assistant_id: Optional[int] = None
    cron_rule: Optional[str] = None

class GenerationSettingRead(GenerationSettingBase):
    id : int
    created_at : datetime
    updated_at : datetime

    class Config:
        from_attributes = True

class GenerationSettingDetail(GenerationSettingRead):
    preset : PresetRead
    assistant : AssistantRead

