from userharbor.interfaces import User

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_user_by_email_returns_matching_user(
    store: SQLAlchemyUserStore,
    existing_user,
) -> None:
    assert store.get_user_by_email("alice@example.com") == User(
        username="alice",
        email="alice@example.com",
        verified=False,
    )


def test_get_user_by_email_returns_none_for_missing_email(
    store: SQLAlchemyUserStore,
    existing_user,
) -> None:
    assert store.get_user_by_email("missing@example.com") is None
