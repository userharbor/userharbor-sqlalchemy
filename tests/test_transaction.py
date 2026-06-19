from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_transaction_commits_all_operations_on_success(
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

    with store.transaction():
        store.create_user(create_user_request)
        store.set_user_verified("alice")
        store.add_session(UserToken("alice", "session-token-hash", expires_at))

    user = session.get(store._models.UserModel, "alice")
    assert user is not None
    assert user.verified is True
    assert session.get(store._models.SessionModel, "session-token-hash") is not None


def test_transaction_rolls_back_all_operations_on_error(
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

    with pytest.raises(RuntimeError, match="abort"):
        with store.transaction():
            store.create_user(create_user_request)
            store.add_session(UserToken("alice", "session-token-hash", expires_at))
            raise RuntimeError("abort")

    assert session.get(store._models.UserModel, "alice") is None
    assert (
        session.get(store._models.EmailVerificationModel, "verification-token-hash")
        is None
    )
    assert session.get(store._models.SessionModel, "session-token-hash") is None


def test_nested_transaction_uses_outer_transaction(
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

    with store.transaction():
        store.create_user(create_user_request)
        with store.transaction():
            store.add_session(UserToken("alice", "session-token-hash", expires_at))

        assert session.get(store._models.UserModel, "alice") is None
        assert session.get(store._models.SessionModel, "session-token-hash") is None

    assert session.get(store._models.UserModel, "alice") is not None
    assert session.get(store._models.SessionModel, "session-token-hash") is not None


def test_transaction_context_is_reset_after_rollback(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    create_user_request = CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=datetime(2030, 1, 1, 12, 0, 0),
    )

    with pytest.raises(RuntimeError):
        with store.transaction():
            store.create_user(create_user_request)
            raise RuntimeError("abort")

    store.create_user(create_user_request)

    assert session.get(store._models.UserModel, "alice") is not None
