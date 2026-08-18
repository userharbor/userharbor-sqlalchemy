from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Protocol

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import MetaData


class UserModelProtocol(Protocol):
    __tablename__: ClassVar[str]
    metadata: ClassVar[MetaData]
    username: Mapped[str]
    username_key: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]
    verified: Mapped[bool]


class TokenModelProtocol(Protocol):
    token_hash: Mapped[str]
    username: Mapped[str]
    expires_at: Mapped[datetime]


class RoleModelProtocol(Protocol):
    role: Mapped[str]


class PermissionModelProtocol(Protocol):
    permission: Mapped[str]


class UserRoleModelProtocol(Protocol):
    username: Mapped[str]
    role: Mapped[str]


class RolePermissionModelProtocol(Protocol):
    role: Mapped[str]
    permission: Mapped[str]


@dataclass(frozen=True)
class Models:
    Base: type[DeclarativeBase]
    UserModel: type[UserModelProtocol]
    EmailVerificationModel: type[TokenModelProtocol]
    SessionModel: type[TokenModelProtocol]
    PasswordResetModel: type[TokenModelProtocol]
    RoleModel: type[RoleModelProtocol]
    PermissionModel: type[PermissionModelProtocol]
    UserRoleModel: type[UserRoleModelProtocol]
    RolePermissionModel: type[RolePermissionModelProtocol]


def create_models(user_model: type[UserModelProtocol] | None = None) -> Models:
    class UserHarborBase(DeclarativeBase):
        pass

    if user_model is not None:
        UserHarborBase.metadata = user_model.metadata

    if not user_model:

        class UserModel(UserHarborBase):
            __tablename__ = "userharbor_users"

            username: Mapped[str] = mapped_column(String(255), primary_key=True)
            username_key: Mapped[str] = mapped_column(
                String(255), unique=True, index=True
            )
            email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
            password_hash: Mapped[str] = mapped_column(String(512))
            verified: Mapped[bool] = mapped_column(Boolean, default=False)

            email_verifications: Mapped[list["EmailVerificationModel"]] = relationship(
                cascade="all, delete-orphan"
            )
            sessions: Mapped[list["SessionModel"]] = relationship(
                cascade="all, delete-orphan"
            )
            password_resets: Mapped[list["PasswordResetModel"]] = relationship(
                cascade="all, delete-orphan"
            )

        user_model = UserModel

    class EmailVerificationModel(UserHarborBase):
        __tablename__ = "userharbor_email_verifications"

        token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
        username: Mapped[str] = mapped_column(
            ForeignKey(f"{user_model.__tablename__}.username", ondelete="CASCADE"),
            index=True,
        )
        expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    class SessionModel(UserHarborBase):
        __tablename__ = "userharbor_sessions"

        token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
        username: Mapped[str] = mapped_column(
            ForeignKey(f"{user_model.__tablename__}.username", ondelete="CASCADE"),
            index=True,
        )
        expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    class PasswordResetModel(UserHarborBase):
        __tablename__ = "userharbor_password_resets"

        token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
        username: Mapped[str] = mapped_column(
            ForeignKey(f"{user_model.__tablename__}.username", ondelete="CASCADE"),
            index=True,
        )
        expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    class RoleModel(UserHarborBase):
        __tablename__ = "userharbor_roles"

        role: Mapped[str] = mapped_column(String(255), primary_key=True)

    class PermissionModel(UserHarborBase):
        __tablename__ = "userharbor_permissions"

        permission: Mapped[str] = mapped_column(String(255), primary_key=True)

    class UserRoleModel(UserHarborBase):
        __tablename__ = "userharbor_user_roles"

        username: Mapped[str] = mapped_column(
            ForeignKey(f"{user_model.__tablename__}.username", ondelete="CASCADE"),
            primary_key=True,
        )
        role: Mapped[str] = mapped_column(
            ForeignKey("userharbor_roles.role", ondelete="CASCADE"),
            primary_key=True,
        )

    class RolePermissionModel(UserHarborBase):
        __tablename__ = "userharbor_role_permissions"

        role: Mapped[str] = mapped_column(
            ForeignKey("userharbor_roles.role", ondelete="CASCADE"),
            primary_key=True,
        )
        permission: Mapped[str] = mapped_column(
            ForeignKey("userharbor_permissions.permission", ondelete="CASCADE"),
            primary_key=True,
        )

    return Models(
        Base=UserHarborBase,
        UserModel=user_model,
        EmailVerificationModel=EmailVerificationModel,
        SessionModel=SessionModel,
        PasswordResetModel=PasswordResetModel,
        RoleModel=RoleModel,
        PermissionModel=PermissionModel,
        UserRoleModel=UserRoleModel,
        RolePermissionModel=RolePermissionModel,
    )
