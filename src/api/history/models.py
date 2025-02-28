from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.api.database.core import Base
from src.api.database.models import TimeStampMixin, MyBaseModel

class History(Base, TimeStampMixin):
    __tablename__ = "history"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt : Mapped[str] = mapped_column(String(2000), nullable=True)
    generation_setting_id : Mapped[int] = mapped_column(ForeignKey("generation_settings.id"), nullable=False, index=True)
    image_url : Mapped[str] = mapped_column(String(500), nullable=True, index=True)
    is_success : Mapped[bool] = mapped_column(nullable=False, default=False)

    generation_setting = relationship("GenerationSetting", back_populates="histories")

class HistoryBase(MyBaseModel):
    prompt : Optional[str] = None
    generation_setting_id : int
    image_url : Optional[str] = None
    is_success : bool

class HistoryCreate(HistoryBase):
    is_success = False

class HistoryUpdate(MyBaseModel):
    is_success: bool

class HistoryRead(HistoryBase):
    id : int
    created_at : datetime
    updated_at : datetime

    class Config:
        from_attributes = True