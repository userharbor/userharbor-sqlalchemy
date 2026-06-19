from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_create_user_persists_user_and_verification_token(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    create_user_request = CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=expires_at,
    )

    store.create_user(create_user_request)

    user = session.get(store._models.UserModel, "alice")
    verification = session.get(
        store._models.EmailVerificationModel,
        "verification-token-hash",
    )

    assert user is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.password_hash == "password-hash"
    assert user.verified is False

    assert verification is not None
    assert verification.username == "alice"
    assert verification.token_hash == "verification-token-hash"
    assert verification.expires_at == create_user_request.expires_at


def test_create_user_rolls_back_when_database_rejects_row(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    create_user_request = CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=expires_at,
    )
    store.create_user(create_user_request)

    duplicate_email = CreateUserRequest(
        username="bob",
        email=create_user_request.email,
        password_hash="other-password-hash",
        verification_token_hash="other-verification-token-hash",
        expires_at=create_user_request.expires_at,
    )

    with pytest.raises(IntegrityError):
        store.create_user(duplicate_email)

    assert session.get(store._models.UserModel, "bob") is None
    assert (
        session.get(
            store._models.EmailVerificationModel,
            "other-verification-token-hash",
        )
        is None
    )
