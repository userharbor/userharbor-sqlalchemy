from userharbor_sqlalchemy.store import SQLAlchemyUserStore

from conftest import get_user


def test_set_user_verified_marks_user_as_verified(
    store: SQLAlchemyUserStore,
    existing_user,
    read_session,
) -> None:
    store.set_user_verified("alice")

    with read_session() as session:
        user = get_user(session)
        assert user is not None
        assert user.verified is True


def test_set_user_verified_ignores_missing_user(
    store: SQLAlchemyUserStore,
    read_session,
) -> None:
    store.set_user_verified("missing")

    with read_session() as session:
        assert get_user(session, "missing") is None
