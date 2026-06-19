from datetime import datetime

from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_password_reset_returns_token(
    store: SQLAlchemyUserStore,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    store.create_user(
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password_hash="password-hash",
            verification_token_hash="verification-token-hash",
            expires_at=expires_at,
        )
    )
    reset = UserToken("alice", "reset-token-hash", expires_at)
    store.set_password_reset(reset)

    assert store.get_password_reset("reset-token-hash") == reset


def test_get_password_reset_returns_none_for_missing_token(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_password_reset("missing") is None
