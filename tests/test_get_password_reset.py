from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_password_reset_returns_token(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
) -> None:
    reset = UserToken("alice", "reset-token-hash", expires_at)
    store.set_password_reset(reset)

    assert store.get_password_reset("reset-token-hash") == reset


def test_get_password_reset_returns_none_for_missing_token(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_password_reset("missing") is None
