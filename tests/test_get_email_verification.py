from userharbor.interfaces import UserToken

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_email_verification_returns_token(
    store: SQLAlchemyUserStore,
    existing_user,
    expires_at,
) -> None:
    assert store.get_email_verification("verification-token-hash") == UserToken(
        username="alice",
        token_hash="verification-token-hash",
        expires_at=expires_at,
    )


def test_get_email_verification_returns_none_for_missing_token(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_email_verification("missing") is None
