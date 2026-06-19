from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_delete_user_removes_user_and_related_tokens(
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
    store.add_session(UserToken("alice", "session-token-hash", expires_at))
    store.set_password_reset(UserToken("alice", "reset-token-hash", expires_at))

    store.delete_user("alice")

    assert session.get(store._models.UserModel, "alice") is None
    assert (
        session.get(store._models.EmailVerificationModel, "verification-token-hash")
        is None
    )
    assert session.get(store._models.SessionModel, "session-token-hash") is None
    assert session.get(store._models.PasswordResetModel, "reset-token-hash") is None


def test_delete_user_ignores_missing_user(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.delete_user("missing")

    assert session.get(store._models.UserModel, "missing") is None
