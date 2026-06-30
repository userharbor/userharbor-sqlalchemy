from datetime import datetime

from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_create_permission_persists_permission(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_permission("users.delete")

    permission = session.get(store._models.PermissionModel, "users.delete")
    assert permission is not None
    assert permission.permission == "users.delete"


def test_delete_permission_deletes_permission_and_assignments(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_role("admin")
    store.create_permission("users.delete")
    store.grant_permission_to_role("admin", "users.delete")

    store.delete_permission("users.delete")

    assert session.get(store._models.PermissionModel, "users.delete") is None
    assert store.get_role_permissions("admin") == set()


def test_delete_permission_ignores_missing_permission(
    store: SQLAlchemyUserStore,
) -> None:
    store.delete_permission("missing.permission")

    assert store.list_permissions() == set()


def test_list_permissions_returns_permissions(store: SQLAlchemyUserStore) -> None:
    store.create_permission("users.read")
    store.create_permission("users.delete")

    assert store.list_permissions() == {"users.read", "users.delete"}


def test_permission_exists_returns_true_for_existing_permission(
    store: SQLAlchemyUserStore,
) -> None:
    store.create_permission("users.delete")

    assert store.permission_exists("users.delete")


def test_permission_exists_returns_false_for_missing_permission(
    store: SQLAlchemyUserStore,
) -> None:
    assert not store.permission_exists("missing.permission")


def test_grant_permission_to_role_persists_assignment(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_role("admin")
    store.create_permission("users.delete")

    store.grant_permission_to_role("admin", "users.delete")
    store.grant_permission_to_role("admin", "users.delete")

    role_permission = session.get(
        store._models.RolePermissionModel,
        ("admin", "users.delete"),
    )
    assert role_permission is not None
    assert store.get_role_permissions("admin") == {"users.delete"}


def test_revoke_permission_from_role_deletes_assignment(
    store: SQLAlchemyUserStore,
    session: Session,
) -> None:
    store.create_role("admin")
    store.create_permission("users.delete")
    store.grant_permission_to_role("admin", "users.delete")

    store.revoke_permission_from_role("admin", "users.delete")
    store.revoke_permission_from_role("admin", "users.delete")

    assert (
        session.get(store._models.RolePermissionModel, ("admin", "users.delete"))
        is None
    )
    assert store.get_role_permissions("admin") == set()


def test_get_user_permissions_returns_permissions_from_roles(
    store: SQLAlchemyUserStore,
) -> None:
    store.create_user(
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password_hash="password-hash",
            verification_token_hash="alice-verification-token-hash",
            expires_at=datetime(2030, 1, 1, 12, 0, 0),
        )
    )
    store.create_role("admin")
    store.create_role("billing")
    store.create_permission("users.delete")
    store.create_permission("invoices.read")
    store.grant_permission_to_role("admin", "users.delete")
    store.grant_permission_to_role("billing", "invoices.read")
    store.grant_role_to_user("alice", "admin")
    store.grant_role_to_user("alice", "billing")

    assert store.get_user_permissions("alice") == {
        "users.delete",
        "invoices.read",
    }


def test_get_user_permissions_returns_empty_set_for_missing_user(
    store: SQLAlchemyUserStore,
) -> None:
    assert store.get_user_permissions("missing") == set()
