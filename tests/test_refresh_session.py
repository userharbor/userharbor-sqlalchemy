from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_refresh_session_updates_expiration(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    new_expires_at = datetime(2030, 1, 2, 12, 0, 0)
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

    store.refresh_session("session-token-hash", new_expires_at)

    user_session = session.get(store._models.SessionModel, "session-token-hash")
    assert user_session is not None
    assert user_session.username == "alice"
    assert user_session.expires_at == new_expires_at


def test_refresh_session_ignores_missing_token(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.refresh_session("missing", datetime(2030, 1, 1, 12, 0, 0))

    assert session.get(store._models.SessionModel, "missing") is None
