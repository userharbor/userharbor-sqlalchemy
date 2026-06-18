from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_session_token


def test_remove_session_deletes_token(
    store: SQLAlchemyUserStore,
    existing_user,
    user_token,
    read_session,
) -> None:
    store.add_session(user_token)

    store.remove_session("token-hash")

    with read_session() as session:
        assert get_session_token(session) is None


def test_remove_session_ignores_missing_token(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.remove_session("missing")

    with read_session() as session:
        assert get_session_token(session, "missing") is None
