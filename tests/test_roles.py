from sqlalchemy.orm import Session

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_create_role_persists_role(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_role("admin")

    role = session.get(store._models.RoleModel, "admin")
    assert role is not None
    assert role.role == "admin"


def test_delete_role_deletes_role_and_assignments(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_user(
        store_create_user_request(
            username="alice",
            email="alice@example.com",
        )
    )
    store.create_role("admin")
    store.create_permission("users.delete")
    store.grant_role_to_user("alice", "admin")
    store.grant_permission_to_role("admin", "users.delete")

    store.delete_role("admin")

    assert session.get(store._models.RoleModel, "admin") is None
    assert store.get_user_roles("alice") == set()
    assert store.get_role_permissions("admin") == set()


def test_delete_role_ignores_missing_role(store: SQLAlchemyUserStore) -> None:
    store.delete_role("missing")

    assert store.list_roles() == set()


def test_list_roles_returns_roles(store: SQLAlchemyUserStore) -> None:
    store.create_role("admin")
    store.create_role("support")

    assert store.list_roles() == {"admin", "support"}


def test_role_exists_returns_true_for_existing_role(
    store: SQLAlchemyUserStore,
) -> None:
    store.create_role("admin")

    assert store.role_exists("admin")


def test_role_exists_returns_false_for_missing_role(
    store: SQLAlchemyUserStore,
) -> None:
    assert not store.role_exists("missing")


def test_grant_role_to_user_persists_assignment(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_user(
        store_create_user_request(
            username="alice",
            email="alice@example.com",
        )
    )
    store.create_role("admin")

    store.grant_role_to_user("alice", "admin")
    store.grant_role_to_user("alice", "admin")

    user_role = session.get(store._models.UserRoleModel, ("alice", "admin"))
    assert user_role is not None
    assert store.get_user_roles("alice") == {"admin"}


def test_revoke_role_from_user_deletes_assignment(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_user(
        store_create_user_request(
            username="alice",
            email="alice@example.com",
        )
    )
    store.create_role("admin")
    store.grant_role_to_user("alice", "admin")

    store.revoke_role_from_user("alice", "admin")
    store.revoke_role_from_user("alice", "admin")

    assert session.get(store._models.UserRoleModel, ("alice", "admin")) is None
    assert store.get_user_roles("alice") == set()


def test_get_user_roles_returns_empty_set_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_user_roles("missing") == set()


def store_create_user_request(username: str, email: str):
    from datetime import datetime

    from userharbor.interfaces import CreateUserRequest

    return CreateUserRequest(
        username=username,
        email=email,
        password_hash="password-hash",
        verification_token_hash=f"{username}-verification-token-hash",
        expires_at=datetime(2030, 1, 1, 12, 0, 0),
    )
