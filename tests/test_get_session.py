from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_session_returns_token(
    store: SQLAlchemyUserStore,
    existing_user,
    user_token: UserToken,
) -> None:
    store.add_session(user_token)

    assert store.get_session("token-hash") == user_token


def test_get_session_returns_none_for_missing_token(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_session("missing") is None
