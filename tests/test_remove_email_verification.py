from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_email_verification


def test_remove_email_verification_deletes_token(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.remove_email_verification("verification-token-hash")

    with read_session() as session:
        assert get_email_verification(session) is None


def test_remove_email_verification_ignores_missing_token(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.remove_email_verification("missing")

    with read_session() as session:
        assert get_email_verification(session) is not None
