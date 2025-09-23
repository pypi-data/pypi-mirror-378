import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bovine.activitystreams.utils import id_for_object

from cattle_grid.dependencies.internals import Transformer
from cattle_grid.model import ActivityMessage as RawActivityMessage
from cattle_grid.database.activity_pub_actor import Actor, Blocking

from cattle_grid.dependencies import (
    AccountExchangePublisher,
    ActivityExchangePublisher,
    SqlSession,
)


from cattle_grid.database.account import ActorForAccount
from cattle_grid.model.account import EventInformation, EventType

logger = logging.getLogger(__name__)


async def should_shovel_activity(session: AsyncSession, activity: dict) -> bool:
    """Some activities like Block or Undo Block should not be visible to the user. This method
    returns False if this is the case."""

    activity_type = activity.get("type")

    if activity_type == "Block":
        return False

    if activity_type == "Undo":
        object_id = id_for_object(activity.get("object"))
        blocking = await session.scalar(
            func.count(
                select(Blocking.id)
                .where(Blocking.request == object_id)
                .scalar_subquery()
            )
        )

        if blocking:
            return False

    return True


async def incoming_shovel(
    msg: RawActivityMessage,
    transformer: Transformer,
    session: SqlSession,
    publisher: ActivityExchangePublisher,
    account_publisher: AccountExchangePublisher,
) -> None:
    """Transfers the message from the RawExchange to the
    Activity- and Account one.

    The message is passed through the transformer.
    """
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == msg.actor)
    )

    if actor_for_account is None:
        logger.warning("Got actor without account %s", msg.actor)
        return

    activity = msg.data

    if not await should_shovel_activity(session, activity):
        return

    # FIXME: Use join to combine the next two queries ...

    db_actor = await session.scalar(select(Actor).where(Actor.actor_id == msg.actor))
    if not db_actor:
        raise ValueError("Actor not found in database")

    blocking = await session.scalar(
        select(Blocking)
        .where(Blocking.actor == db_actor)
        .where(Blocking.blocking == activity.get("actor"))
        .where(Blocking.active)
    )
    if blocking:
        return

    account_name = actor_for_account.account.name
    to_shovel = await transformer({"raw": msg.data})
    activity_type = msg.data.get("type")

    await account_publisher(
        EventInformation(
            actor=msg.actor,
            event_type=EventType.incoming,
            data=to_shovel,
        ),
        routing_key=f"receive.{account_name}.incoming",
    )

    await publisher(
        {
            "actor": msg.actor,
            "data": to_shovel,
        },
        routing_key=f"incoming.{activity_type}",
    )


async def outgoing_shovel(
    msg: RawActivityMessage,
    transformer: Transformer,
    session: SqlSession,
    publisher: ActivityExchangePublisher,
    account_publisher: AccountExchangePublisher,
) -> None:
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == msg.actor)
    )

    logger.debug("OUTGOING SHOVEL")

    if actor_for_account is None:
        logger.warning("Actor %s for account not found", msg.actor)
        return

    account_name = actor_for_account.account.name
    to_shovel = await transformer({"raw": msg.data})
    activity_type = msg.data.get("type")

    await account_publisher(
        EventInformation(
            actor=msg.actor,
            event_type=EventType.outgoing,
            data=to_shovel,
        ),
        routing_key=f"receive.{account_name}.outgoing",
    )

    await publisher(
        {
            "actor": msg.actor,
            "data": to_shovel,
        },
        routing_key=f"outgoing.{activity_type}",
    )
