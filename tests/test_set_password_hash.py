import pytest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_user


def test_set_password_hash_updates_stored_hash(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.set_password_hash("alice", "new-password-hash")

    with read_session() as session:
        user = get_user(session)
        assert user is not None
        assert user.password_hash == "new-password-hash"


def test_set_password_hash_raises_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    with pytest.raises(KeyError, match="User not found: missing"):
        store.set_password_hash("missing", "new-password-hash")
