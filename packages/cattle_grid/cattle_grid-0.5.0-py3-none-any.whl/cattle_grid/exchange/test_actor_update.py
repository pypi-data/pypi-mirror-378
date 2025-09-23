from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.account import ActorForAccount
from cattle_grid.model.exchange_update_actor import UpdateAction, UpdateActionType

from .actor_update import handle_actor_action


async def test_handle_actor_action_rename(
    actor_for_test, account_for_test, sql_session
):
    actor_for_account = ActorForAccount(
        actor=actor_for_test.actor_id, account=account_for_test
    )
    sql_session.add(actor_for_account)
    await sql_session.commit()

    action = UpdateAction(
        action=UpdateActionType.rename,
        name="new name",  # type:ignore
    )

    await handle_actor_action(actor_for_test, sql_session, action)

    await sql_session.refresh(actor_for_account)

    assert actor_for_account.name == "new name"
