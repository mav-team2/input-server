import asyncio
import logging
from typing import Annotated, Any, Union

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession, \
    async_scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, declared_attr
from google.cloud.sql.connector import Connector, IPTypes
# import pymysql
import aiomysql
from starlette.requests import Request

from src.api import config
from src.api.database.exceptions import NotFoundError

log = logging.getLogger(__name__)

# def connect_with_connector(**kwargs) -> AsyncEngine:
#     """
#     Initializes a connection pool for a Cloud SQL instance of MySQL.
#
#     Uses the Cloud SQL Python Connector package.
#     """
#     # Note: Saving credentials in environment variables is convenient, but not
#     # secure - consider a more secure solution such as
#     # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
#     # keep secrets safe.
#
#     if config.ENV == 'local':
#         return create_async_engine(
#             config.LOCAL_DATABASE_URL,
#             **kwargs
#         )
#
#     if config.ENV == "development":
#         ip_type = IPTypes.PUBLIC
#     else:
#         ip_type = IPTypes.PRIVATE
#
#     connector = Connector(ip_type)
#
#     def getconn() -> aiomysql.connections.Connection:
#         conn: aiomysql.connections.Connection = connector.connect(
#             config.GCP_INSTANCE_CONNECTION_NAME,
#             "aiomysql",
#             user=config.DATABASE_USER,
#             password=config.DATABASE_PASSWORD,
#             db=config.DATABASE_NAME,
#         )
#         return conn
#
#     # pool = create_engine(
#     #     "mysql+pymysql://",
#     #     creator=getconn,
#     #     **kwargs
#     #     # ...
#     # )
#
#     pool = create_async_engine(
#         "mysql+pymysql://",
#         creator=getconn,
#         **kwargs
#     )
#
#     return pool


# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CustomBase:
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


    @property
    def _id_str(self):
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in " "__repr__attrs__".format(
                        self.__class__, key
                    )
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self):
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


Base = declarative_base(cls=CustomBase)


if config.ENV == 'local':
    engine = create_async_engine(
        config.LOCAL_DATABASE_URL,
        pool_size=config.DATABASE_ENGINE_POOL_SIZE,
        max_overflow=config.DATABASE_ENGINE_MAX_OVERFLOW,
        pool_pre_ping=config.DATABASE_ENGINE_POOL_PING,
    )
else:
    engine = create_async_engine(
        config.DATABASE_URL,
        pool_size=config.DATABASE_ENGINE_POOL_SIZE,
        max_overflow=config.DATABASE_ENGINE_MAX_OVERFLOW,
        pool_pre_ping=config.DATABASE_ENGINE_POOL_PING,
    )


async def get_db() -> AsyncSession:
    session = async_scoped_session(async_sessionmaker(bind=engine), scopefunc=asyncio.current_task)
    log.debug("current session: %s", session)

    try:
        yield session
    finally:
        await session.remove()


DbSession = Annotated[Union[Session, AsyncSession], Depends(get_db)]


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name):
        for c in Base.registry._class_registry.values():
            if hasattr(c, "__table__"):
                if c.__table__.fullname.lower() == name.lower():
                    return c

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    if not mapped_class:
        raise NotFoundError(BaseModel)

    return mapped_class
