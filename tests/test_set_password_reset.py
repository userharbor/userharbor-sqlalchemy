from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_set_password_reset_persists_token(
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
    store.set_password_reset(UserToken("alice", "reset-token-hash", expires_at))

    reset = session.get(store._models.PasswordResetModel, "reset-token-hash")
    assert reset is not None
    assert reset.username == "alice"
    assert reset.expires_at == expires_at
