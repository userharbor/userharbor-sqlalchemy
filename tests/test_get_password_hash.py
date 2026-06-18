import pytest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_get_password_hash_returns_stored_hash(
    store: SQLAlchemyUserStore,
    existing_user,
) -> None:
    assert store.get_password_hash("alice") == "password-hash"


def test_get_password_hash_raises_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    with pytest.raises(KeyError, match="User not found: missing"):
        store.get_password_hash("missing")
