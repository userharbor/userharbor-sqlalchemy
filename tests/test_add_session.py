from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_session_token


def test_add_session_persists_session_token(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
    read_session,
) -> None:
    store.add_session(UserToken("alice", "session-token-hash", expires_at))

    with read_session() as session:
        user_session = get_session_token(session, "session-token-hash")
        assert user_session is not None
        assert user_session.username == "alice"
        assert user_session.expires_at == expires_at
