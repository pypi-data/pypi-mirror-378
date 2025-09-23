import pytest

from unittest.mock import AsyncMock

from cattle_grid.model import ActivityMessage
from cattle_grid.activity_pub.actor import create_actor
from cattle_grid.database.activity_pub_actor import Blocking
from cattle_grid.testing.fixtures import *  # noqa

from .shovel import incoming_shovel, should_shovel_activity


async def fake_transformer(a):
    return a


async def test_incoming_message(sql_session, actor_with_account):
    publisher = AsyncMock()
    account_publisher = AsyncMock()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=actor_with_account.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(
        activity,
        fake_transformer,
        session=sql_session,
        publisher=publisher,
        account_publisher=account_publisher,
    )

    publisher.assert_awaited_once()
    account_publisher.assert_awaited_once()

    args = publisher.call_args[0]
    result = args[0]

    assert result["data"]["raw"]["@context"] == activity_pub["@context"]


async def test_incoming_block(sql_session, actor_with_account):
    publisher = AsyncMock()
    account_publisher = AsyncMock()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Block",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(actor=actor_with_account.actor_id, data=activity_pub)

    await incoming_shovel(
        activity,
        fake_transformer,
        session=sql_session,
        publisher=publisher,
        account_publisher=account_publisher,
    )

    publisher.assert_not_awaited()


async def test_incoming_from_blocked_user(sql_session, actor_with_account):
    publisher = AsyncMock()
    account_publisher = AsyncMock()

    remote_actor = "http://remote.test/actor"

    sql_session.add(
        Blocking(
            actor=actor_with_account,
            blocking=remote_actor,
            request="http://blocked.test/id",
            active=True,
        )
    )
    await sql_session.commit()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": remote_actor,
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=actor_with_account.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(
        activity,
        fake_transformer,
        session=sql_session,
        publisher=publisher,
        account_publisher=account_publisher,
    )
    publisher.assert_not_awaited()


async def test_incoming_from_blocked_user_inactive_block(
    sql_session, actor_with_account
):
    publisher = AsyncMock()
    account_publisher = AsyncMock()
    remote_actor = "http://remote.test/actor"

    sql_session.add(
        Blocking(
            actor=actor_with_account,
            blocking=remote_actor,
            request="http://blocked.test/id",
            active=False,
        )
    )
    await sql_session.commit()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": remote_actor,
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=actor_with_account.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(
        activity,
        fake_transformer,
        session=sql_session,
        publisher=publisher,
        account_publisher=account_publisher,
    )
    publisher.assert_awaited_once()
    account_publisher.assert_awaited_once()


async def test_incoming_message_non_gateway_actor(sql_session):
    actor = await create_actor(
        sql_session, "http://localhost/", preferred_username="bob"
    )
    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    publisher = AsyncMock()
    account_publisher = AsyncMock()
    activity = ActivityMessage(
        actor=actor.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(
        activity,
        fake_transformer,
        session=sql_session,
        publisher=publisher,
        account_publisher=account_publisher,
    )
    publisher.assert_not_awaited()


@pytest.mark.parametrize(
    "activity, expected",
    [
        (
            {
                "type": "Activity",
            },
            True,
        ),
        (
            {
                "type": "Block",
            },
            False,
        ),
        (
            {"type": "Undo", "object": "http://follow.test/id"},
            True,
        ),
    ],
)
async def test_should_shovel_activity(sql_session, activity, expected):
    result = await should_shovel_activity(sql_session, activity)

    assert result == expected


@pytest.mark.parametrize("active, expected", [(True, False), (False, False)])
async def test_should_shovel_activity_undo(
    sql_session, actor_with_account, active, expected
):
    block_id = "http://block.test/id"
    activity = {"type": "Undo", "object": block_id}

    sql_session.add(
        Blocking(
            actor=actor_with_account,
            blocking="http://remote.test",
            request=block_id,
            active=active,
        )
    )
    await sql_session.commit()

    result = await should_shovel_activity(sql_session, activity)

    assert result == expected
