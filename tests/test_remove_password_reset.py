from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_password_reset


def test_remove_password_reset_deletes_token(
    store: SQLAlchemyUserStore,
    existing_user,
    user_token,
    read_session,
) -> None:
    store.set_password_reset(user_token)

    store.remove_password_reset("token-hash")

    with read_session() as session:
        assert get_password_reset(session) is None


def test_remove_password_reset_ignores_missing_token(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.remove_password_reset("missing")

    with read_session() as session:
        assert get_password_reset(session, "missing") is None
