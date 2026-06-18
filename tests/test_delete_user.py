from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import (
    get_email_verification,
    get_password_reset,
    get_session_token,
    get_user,
)


def test_delete_user_removes_user_and_related_tokens(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
    read_session,
) -> None:
    store.add_session(UserToken("alice", "session-token-hash", expires_at))
    store.set_password_reset(UserToken("alice", "reset-token-hash", expires_at))

    store.delete_user("alice")

    with read_session() as session:
        assert get_user(session) is None
        assert get_email_verification(session) is None
        assert get_session_token(session, "session-token-hash") is None
        assert get_password_reset(session, "reset-token-hash") is None


def test_delete_user_ignores_missing_user(
    store: SQLAlchemyUserStore,
    read_session,
) -> None:
    store.delete_user("missing")

    with read_session() as session:
        assert get_user(session, "missing") is None
