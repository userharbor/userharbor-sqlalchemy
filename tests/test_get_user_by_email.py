from datetime import datetime

from userharbor.interfaces import CreateUserRequest, User

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_user_by_email_returns_matching_user(
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

    assert store.get_user_by_email("alice@example.com") == User(
        username="alice",
        email="alice@example.com",
        verified=False,
    )


def test_get_user_by_email_returns_none_for_missing_email(
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

    assert store.get_user_by_email("missing@example.com") is None
