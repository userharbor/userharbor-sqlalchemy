from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_nested_transaction_changes_are_hidden_until_outer_commit(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    request = CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=expires_at,
    )

    with store.transaction():
        store.create_user(request)
        with store.transaction():
            store.add_session(
                UserToken("alice", "session-token-hash", expires_at)
            )

        assert session.get(store._models.UserModel, "alice") is None
        assert session.get(store._models.SessionModel, "session-token-hash") is None

    assert session.get(store._models.UserModel, "alice") is not None
    assert session.get(store._models.SessionModel, "session-token-hash") is not None
