import enum
from datetime import datetime
from typing import Optional, Any, Dict

from sqlalchemy import Column, String, Integer, JSON, Enum
from sqlalchemy.orm import relationship

from src.api.database.core import Base
from src.api.database.models import MyBaseModel, TimeStampMixin


# Enum 정의
class APIType(str, enum.Enum):
    T2I = "T2I"
    I2I = "I2I"


# SQLAlchemy 모델
class Preset(Base, TimeStampMixin):
    __tablename__ = "preset"

    id = Column(Integer, primary_key=True, index=True)
    parameter = Column(JSON, nullable=False)
    description = Column(String(200), nullable=True)
    api_type = Column(Enum(APIType), nullable=False, default=APIType.I2I)

    generation_settings = relationship("GenerationSetting", back_populates="preset")
    # calls = relationship("Call", back_populates="preset")


class PresetBase(MyBaseModel):
    parameter: Dict[str, Any]
    description: Optional[str] = None
    api_type: APIType
    # thread_id_id : Optional[int] = None


class PresetCreate(PresetBase):
    pass


class PresetUpdate(PresetBase):
    pass

class PresetRead(PresetBase):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
