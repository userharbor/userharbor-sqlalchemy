from userharbor.interfaces import User

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_user_by_username_returns_user_without_password_hash(
    store: SQLAlchemyUserStore,
    existing_user,
) -> None:
    assert store.get_user_by_username("alice") == User(
        username="alice",
        email="alice@example.com",
        verified=False,
    )


def test_get_user_by_username_returns_none_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_user_by_username("missing") is None
