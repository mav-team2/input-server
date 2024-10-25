from typing import Any, Type

from pydantic import BaseModel
from pydantic.errors import PydanticErrorMixin
from sqlalchemy.exc import DatabaseError


class NotFoundError(PydanticErrorMixin, DatabaseError):
    """Raised when a resource is not found in the database."""
    def __init__(self, model: Type[BaseModel]) -> None:
        super().__init__(f"{model.__name__} not found")
        self.code = "not_found"
        self.message = f"{model.__name__} not found"