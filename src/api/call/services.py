import logging
from typing import Optional, Type

from sqlalchemy import select
from sqlalchemy.orm import joinedload, Query

from src.api.call.models import Call, CallCreate
from src.api.database.core import DbSession

log = logging.getLogger(__name__)


async def get(*, db_session: DbSession, call_id: int) -> Optional[Call]:
    """Returns a user based on the given user id."""
    # return db_session.query(Call).options(joinedload(Call.preset)).filter(Call.id == call_id).one_or_none()
    return (await db_session.execute(select(Call).join(Call.preset).where(Call.id == call_id))).scalar_one_or_none()


async def get_all(*, db_session: DbSession) -> Query[Type[Call]]:
    return (await db_session.execute(select(Call))).scalars().all()


async def create(*, db_session: DbSession, call_in: CallCreate) -> Call:
    """Creates a new user."""
    # call = Call(**call_in.model_dump(exclude={"user_id"}), user=user)
    call = Call(**call_in.model_dump())
    db_session.add(call)
    await db_session.commit()
    await db_session.refresh(call)
    return call


def delete(*, db_session: DbSession, call_id: int):
    """Deletes an existing entity."""
    entity = db_session.query(Call).filter(Call.id == call_id).one()
    db_session.delete(entity)
    db_session.commit()


# background task for call
def generate(prompt: str) -> Call:
    pass
    # generate new prompt
