from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.api.database.core import Base
from src.api.database.models import TimeStampMixin, MyBaseModel


class Assistant(Base, TimeStampMixin):
    __tablename__ = "assistant"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assistant_id : Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Assistant ID for chatGPT api")
    description : Mapped[str] = mapped_column(String(500), nullable=True)

    generation_settings = relationship("GenerationSetting", back_populates="assistant")


class AssistantBase(MyBaseModel):
    assistant_id: str
    description: Optional[str] = None


class AssistantCreate(AssistantBase):
    pass


class AssistantRead(AssistantBase):
    id : int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]