from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_remove_all_sessions_deletes_only_users_sessions(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    expires_at = datetime(2030, 1, 1, 12, 0, 0)
    store.create_user(
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password_hash="password-hash",
            verification_token_hash="alice-verification-token-hash",
            expires_at=expires_at,
        )
    )
    store.create_user(
        CreateUserRequest(
            username="bob",
            email="bob@example.com",
            password_hash="bob-password-hash",
            verification_token_hash="bob-verification-token-hash",
            expires_at=expires_at,
        )
    )
    store.add_session(UserToken("alice", "alice-session-1", expires_at))
    store.add_session(UserToken("alice", "alice-session-2", expires_at))
    store.add_session(UserToken("bob", "bob-session", expires_at))

    store.remove_all_sessions("alice")

    alice_sessions = list(
        session.scalars(
            select(store._models.SessionModel).where(
                store._models.SessionModel.username == "alice"
            )
        )
    )
    bob_sessions = list(
        session.scalars(
            select(store._models.SessionModel).where(
                store._models.SessionModel.username == "bob"
            )
        )
    )

    assert alice_sessions == []
    assert [session_token.token_hash for session_token in bob_sessions] == [
        "bob-session"
    ]
