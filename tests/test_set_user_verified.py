from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_set_user_verified_marks_user_as_verified(
    store: SQLAlchemyUserStore,
    session: Session,
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

    store.set_user_verified("alice")

    user = session.get(store._models.UserModel, "alice")
    assert user is not None
    assert user.verified is True


def test_set_user_verified_ignores_missing_user(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.set_user_verified("missing")

    assert session.get(store._models.UserModel, "missing") is None
