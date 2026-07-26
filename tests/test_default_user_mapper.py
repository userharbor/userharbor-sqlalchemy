from datetime import datetime

from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_default_user_mapper_does_not_expose_password_hash(
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

    user = store.get_user_by_username("alice")

    assert user is not None
    assert not hasattr(user, "password_hash")
