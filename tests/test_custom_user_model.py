from dataclasses import dataclass
from datetime import datetime
from typing import cast

from sqlalchemy import Boolean, String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool
from userharbor.interfaces import CreateUserRequest

from userharbor_sqlalchemy.models import UserModelProtocol
from userharbor_sqlalchemy.store import SQLAlchemyUserStore


class AppBase(DeclarativeBase):
    pass


class AppUser(AppBase):
    __tablename__ = "app_users"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    username_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    display_name: Mapped[str] = mapped_column(String(255), default="Anonymous")


@dataclass
class AppPublicUser:
    username: str
    email: str
    verified: bool
    display_name: str


def test_store_uses_custom_user_model_and_mapper() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def map_app_user(model: UserModelProtocol) -> AppPublicUser:
        app_user = cast(AppUser, model)
        return AppPublicUser(
            username=app_user.username,
            email=app_user.email,
            verified=app_user.verified,
            display_name=app_user.display_name,
        )

    store = SQLAlchemyUserStore(
        sessionmaker(bind=engine),
        user_model=AppUser,
        user_mapper=map_app_user,
    )
    store.metadata.create_all(engine)

    try:
        expires_at = datetime(2030, 1, 1, 12, 0, 0)
        store.create_user(
            CreateUserRequest(
                username="alice",
                email="alice@example.com",
                password_hash="password-hash",
                verification_token_hash="verification-token-hash",
                expires_at=expires_at,
            )
        )
        store.set_user_verified("alice")

        with store._session_factory() as session:
            app_user = session.get(AppUser, "alice")
            assert app_user is not None
            assert app_user.username_key == "alice"
            assert app_user.password_hash == "password-hash"

        assert store.get_user_by_username("ALICE") == AppPublicUser(
            username="alice",
            email="alice@example.com",
            verified=True,
            display_name="Anonymous",
        )
        assert store.get_user_by_email("alice@example.com") == AppPublicUser(
            username="alice",
            email="alice@example.com",
            verified=True,
            display_name="Anonymous",
        )
        assert store.get_email_verification("verification-token-hash") is not None

        store.create_role("admin")
        store.create_permission("users.delete")
        store.grant_permission_to_role("admin", "users.delete")
        store.grant_role_to_user("alice", "admin")

        assert store.get_user_roles("alice") == {"admin"}
        assert store.get_user_permissions("alice") == {"users.delete"}
    finally:
        store.metadata.drop_all(engine)
        engine.dispose()
