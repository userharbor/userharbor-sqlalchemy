from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_password_reset


def test_set_password_reset_persists_token(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
    read_session,
) -> None:
    store.set_password_reset(UserToken("alice", "reset-token-hash", expires_at))

    with read_session() as session:
        reset = get_password_reset(session, "reset-token-hash")
        assert reset is not None
        assert reset.username == "alice"
        assert reset.expires_at == expires_at
