from datetime import datetime

from userharbor.interfaces import CreateUserRequest, User

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_user_by_username_returns_user_without_password_hash(
    store: SQLAlchemyUserStore,
) -> None:
    store.create_user(
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password_hash="password-hash",
            verification_token_hash="verification-token-hash",
            expires_at=datetime(2030, 1, 1, 12, 0, 0),
        )
    )

    assert store.get_user_by_username("alice") == User(
        username="alice",
        email="alice@example.com",
        verified=False,
    )


def test_get_user_by_username_returns_none_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_user_by_username("missing") is None
