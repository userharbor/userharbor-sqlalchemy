from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_set_email_verification_persists_token(
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
    store.set_email_verification(UserToken("alice", "new-verification-token", expires_at))

    verification = session.get(
        store._models.EmailVerificationModel,
        "new-verification-token",
    )
    assert verification is not None
    assert verification.username == "alice"
    assert verification.expires_at == expires_at
