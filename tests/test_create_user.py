import pytest
from sqlalchemy.exc import IntegrityError
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_email_verification, get_user


def test_create_user_persists_user_and_verification_token(
    store: SQLAlchemyUserStore,
    create_user_request: CreateUserRequest,
    read_session,
) -> None:
    store.create_user(create_user_request)

    with read_session() as session:
        user = get_user(session)
        verification = get_email_verification(session)

        assert user is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.password_hash == "password-hash"
        assert user.verified is False

        assert verification is not None
        assert verification.username == "alice"
        assert verification.token_hash == "verification-token-hash"
        assert verification.expires_at == create_user_request.expires_at


def test_create_user_rolls_back_when_database_rejects_row(
    store: SQLAlchemyUserStore,
    create_user_request: CreateUserRequest,
    read_session,
) -> None:
    store.create_user(create_user_request)

    duplicate_email = CreateUserRequest(
        username="bob",
        email=create_user_request.email,
        password_hash="other-password-hash",
        verification_token_hash="other-verification-token-hash",
        expires_at=create_user_request.expires_at,
    )

    with pytest.raises(IntegrityError):
        store.create_user(duplicate_email)

    with read_session() as session:
        assert get_user(session, "bob") is None
        assert get_email_verification(session, "other-verification-token-hash") is None
