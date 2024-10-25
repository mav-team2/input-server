# from typing import Optional
#
# import bcrypt
# from pydantic import field_validator, Field
#
# from sqlalchemy import Boolean, Column, String, LargeBinary
#
# from src.api.database.database import Base
# from src.api.models import MyBaseModel, TimeStampMixin
#
#
# def hash_password(password: str) -> bytes:
#     """Generates a hashed version of the provided password."""
#     pw = bytes(password, "utf-8")
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(pw, salt)
#
#
# class User(Base, TimeStampMixin):
#     __tablename__ = "users"
#
#     id = Column(String(20), primary_key=True, index=True)
#     login_id = Column(String(20), unique=True, index=True, nullable=False)
#     password = Column(LargeBinary, nullable=False)
#     is_active = Column(Boolean, nullable=False, default=False)
#     is_admin = Column(Boolean, nullable=False, default=False)
#
#     def check_password(self, password):
#         return bcrypt.checkpw(password.encode("utf-8"), self.password)
#
#
# class UserBase(MyBaseModel):
#     login_id: str
#     is_active: bool
#
#
# class UserLogin(UserBase):
#     password: str
#
#     @classmethod
#     @field_validator("password")
#     def password_required(cls, v):
#         if not v:
#             raise ValueError("Must not be empty string")
#         return v
#
#
# class UserRegister(UserLogin):
#     @classmethod
#     @field_validator("password", "login_id")
#     def login_id_required(cls, v) -> str:
#         if not v:
#             raise ValueError("Must not be empty string")
#         return v
#
#     @classmethod
#     @field_validator("password", mode='before')
#     def password_required(cls, v: str) -> bytes:
#         # we generate a password for those that don't have one
#         return hash_password(v)
#
#
# class UserUpdate(MyBaseModel):
#     id: int
#     password: Optional[str] = Field(None)
#     is_active: Optional[bool]
#     is_admin: Optional[bool]
#
#     @classmethod
#     @field_validator("password", mode="before")
#     def hash(cls, v):
#         return hash_password(str(v))
