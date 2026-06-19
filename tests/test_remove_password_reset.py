from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_remove_password_reset_deletes_token(
    store: SQLAlchemyUserStore,
    session: Session,
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
    user_token = UserToken("alice", "token-hash", expires_at)
    store.set_password_reset(user_token)

    store.remove_password_reset("token-hash")

    assert session.get(store._models.PasswordResetModel, "token-hash") is None


def test_remove_password_reset_ignores_missing_token(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.remove_password_reset("missing")

    assert session.get(store._models.PasswordResetModel, "missing") is None
