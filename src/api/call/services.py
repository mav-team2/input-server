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

def get_is_done(*, db_session: Session, call_id: int) -> Optional[bool]:
    call = get(db_session=db_session, call_id=call_id)

    if call:
        if call.result_url is None:
            return False
        else:
            return True


async def get_all(*, db_session: DbSession) -> Query[Type[Call]]:
    return (await db_session.execute(select(Call))).scalars().all()


async def create(*, db_session: DbSession, call_in: CallCreate) -> Call:
    """Creates a new user."""
    # user = user_service.get_by_id(db_session=db_session, user_id=history_in.user_id)
    # add preset_id

    # call = Call(**call_in.model_dump(exclude={"user_id"}), user=user)
    call = Call(**call_in.model_dump())
    await db_session.add(call)
    await db_session.commit()
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
