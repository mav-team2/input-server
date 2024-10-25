import logging
import os
from typing import List

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

log = logging.getLogger(__name__)


def get_env_tags(tag_list: List[str]) -> dict:
    """Create dictionary of available env tags."""
    tags = {}
    for t in tag_list:
        tag_key, env_key = t.split(":")

        env_value = os.environ.get(env_key)

        if env_value:
            tags.update({tag_key: env_value})

    return tags


config = Config(".env")


ENV = config("ENV")
LOG_LEVEL = config("LOG_LEVEL", default='warning') if ENV == 'production' else config("LOG_LEVEL", default='debug')

UI_URL = config("UI_URL", default="http://localhost:8080")




# sentry middleware
# SENTRY_ENABLED = config("SENTRY_ENABLED", default="")
# SENTRY_DSN = config("SENTRY_DSN", default="")
# SENTRY_APP_KEY = config("SENTRY_APP_KEY", default="")
# SENTRY_TAGS = config("SENTRY_TAGS", default="")


# static files
DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), os.path.join("static", "dist")
)
STATIC_DIR = config("STATIC_DIR", default=DEFAULT_STATIC_DIR)

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_USER = config("DATABASE_USER", default="root")
DATABASE_PASSWORD = config("DATABASE_PASSWORD")
DATABASE_NAME = config("DATABASE_NAME", default="api")
DATABASE_PORT = config("DATABASE_PORT", default="3306")
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=20)
DATABASE_ENGINE_MAX_OVERFLOW = config("DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=0)
DATABASE_URL = config("DATABASE_URL")


# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING = config("DATABASE_ENGINE_POOL_PING", default=False)
SQLALCHEMY_DATABASE_URI = f"mysql+aiomysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
DEV_SQLALCHEMY_DATABASE_URI = config("DEV_SQLALCHEMY_DATABASE_URI", default=SQLALCHEMY_DATABASE_URI)
LOCAL_DATABASE_URL = config("LOCAL_DATABASE_URL", default=SQLALCHEMY_DATABASE_URI)
# ALEMBIC_CORE_REVISION_PATH = config(
#     "ALEMBIC_CORE_REVISION_PATH",
#     default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/core",
# )
# ALEMBIC_TENANT_REVISION_PATH = config(
#     "ALEMBIC_TENANT_REVISION_PATH",
#     default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/tenant",
# )

# GCP SQL Connection
GCP_INSTANCE_CONNECTION_NAME = config("GCP_INSTANCE_CONNECTION_NAME")
GCP_IP_TYPE = config("GCP_IP_TYPE", default="PRIVATE")

ALEMBIC_INI_PATH = config(
    "ALEMBIC_INI_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/alembic.ini",
)
# ALEMBIC_MULTI_TENANT_MIGRATION_PATH = config(
#     "ALEMBIC_MULTI_TENANT_MIGRATION_PATH",
#     default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/multi-tenant-migration.sql",
# )


OPENAI_API_KEY = config("OPENAI_API_KEY")

vector_key_file = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), '../', 'vector_store_ids.txt'
)

if os.path.exists(vector_key_file):
    with open(vector_key_file, 'r') as file:
        VECTOR_STORE_IDS = file.read().splitlines()
else:
    VECTOR_STORE_IDS = config("VECTOR_STORE_IDS", cast=CommaSeparatedStrings, default=None)

RABBITMQ_URL = config("RABBITMQ_URL")
RABBITMQ_EXCHANGE = config("RABBITMQ_EXCHANGE")
RABBITMQ_ROUTING_KEY = config("RABBITMQ_ROUTING_KEY")
RABBITMQ_QUEUE = config("RABBITMQ_QUEUE")


