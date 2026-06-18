import pytest
from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_email_verification, get_session_token, get_user


def test_transaction_commits_all_operations_on_success(
    store: SQLAlchemyUserStore,
    create_user_request,
    expires_at,
    read_session,
) -> None:
    with store.transaction():
        store.create_user(create_user_request)
        store.set_user_verified("alice")
        store.add_session(UserToken("alice", "session-token-hash", expires_at))

    with read_session() as session:
        user = get_user(session)
        assert user is not None
        assert user.verified is True
        assert get_session_token(session, "session-token-hash") is not None


def test_transaction_rolls_back_all_operations_on_error(
    store: SQLAlchemyUserStore,
    create_user_request,
    expires_at,
    read_session,
) -> None:
    with pytest.raises(RuntimeError, match="abort"):
        with store.transaction():
            store.create_user(create_user_request)
            store.add_session(UserToken("alice", "session-token-hash", expires_at))
            raise RuntimeError("abort")

    with read_session() as session:
        assert get_user(session) is None
        assert get_email_verification(session) is None
        assert get_session_token(session, "session-token-hash") is None


def test_nested_transaction_uses_outer_transaction(
    store: SQLAlchemyUserStore,
    create_user_request,
    expires_at,
    read_session,
) -> None:
    with store.transaction():
        store.create_user(create_user_request)
        with store.transaction():
            store.add_session(UserToken("alice", "session-token-hash", expires_at))

        with read_session() as session:
            assert get_user(session) is None
            assert get_session_token(session, "session-token-hash") is None

    with read_session() as session:
        assert get_user(session) is not None
        assert get_session_token(session, "session-token-hash") is not None


def test_transaction_context_is_reset_after_rollback(
    store: SQLAlchemyUserStore,
    create_user_request,
    read_session,
) -> None:
    with pytest.raises(RuntimeError):
        with store.transaction():
            store.create_user(create_user_request)
            raise RuntimeError("abort")

    store.create_user(create_user_request)

    with read_session() as session:
        assert get_user(session) is not None
