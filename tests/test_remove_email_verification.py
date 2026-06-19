from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_remove_email_verification_deletes_token(
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

    store.remove_email_verification("verification-token-hash")

    assert (
        session.get(store._models.EmailVerificationModel, "verification-token-hash")
        is None
    )


def test_remove_email_verification_ignores_missing_token(
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

    store.remove_email_verification("missing")

    assert (
        session.get(store._models.EmailVerificationModel, "verification-token-hash")
        is not None
    )
