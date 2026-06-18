from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_email_verification


def test_set_email_verification_persists_token(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
    read_session,
) -> None:
    store.set_email_verification(UserToken("alice", "new-verification-token", expires_at))

    with read_session() as session:
        verification = get_email_verification(session, "new-verification-token")
        assert verification is not None
        assert verification.username == "alice"
        assert verification.expires_at == expires_at
