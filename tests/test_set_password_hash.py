from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_set_password_hash_updates_stored_hash(
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

    store.set_password_hash("alice", "new-password-hash")

    user = session.get(store._models.UserModel, "alice")
    assert user is not None
    assert user.password_hash == "new-password-hash"


def test_set_password_hash_raises_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    with pytest.raises(KeyError, match="User not found: missing"):
        store.set_password_hash("missing", "new-password-hash")
