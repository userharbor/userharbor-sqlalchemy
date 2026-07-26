from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_create_user_raises_integrity_error_for_duplicate_email(
    store: SQLAlchemyUserStore,
) -> None:
    request = CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=datetime(2030, 1, 1, 12, 0, 0),
    )
    store.create_user(request)

    duplicate_email = CreateUserRequest(
        username="bob",
        email=request.email,
        password_hash="other-password-hash",
        verification_token_hash="other-verification-token-hash",
        expires_at=request.expires_at,
    )

    with pytest.raises(IntegrityError):
        store.create_user(duplicate_email)
