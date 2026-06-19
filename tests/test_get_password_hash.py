from datetime import datetime

import pytest
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_password_hash_returns_stored_hash(
    store: SQLAlchemyUserStore,
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

    assert store.get_password_hash("alice") == "password-hash"


def test_get_password_hash_raises_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    with pytest.raises(KeyError, match="User not found: missing"):
        store.get_password_hash("missing")
