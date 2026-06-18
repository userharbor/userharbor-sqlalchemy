from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import list_sessions


def test_remove_all_sessions_deletes_only_users_sessions(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
    read_session,
) -> None:
    store.create_user(
        type(existing_user)(
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

    with read_session() as session:
        assert list_sessions(session, "alice") == []
        bob_sessions = list_sessions(session, "bob")
        assert [session_token.token_hash for session_token in bob_sessions] == [
            "bob-session"
        ]
