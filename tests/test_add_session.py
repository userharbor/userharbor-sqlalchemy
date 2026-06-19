from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_add_session_persists_session_token(
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

    user_session = session.get(store._models.SessionModel, "session-token-hash")
    assert user_session is not None
    assert user_session.username == "alice"
    assert user_session.expires_at == expires_at
