from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Protocol, TypeVar, cast

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    InstrumentedAttribute,
    Mapped,
    Mapper,
    declared_attr,
    mapped_column,
    registry,
    relationship,
)
from sqlalchemy.schema import MetaData


class UserModelProtocol(Protocol):
    """Values exposed by a user model instance."""

    username: str
    username_key: str
    email: str
    password_hash: str
    verified: bool


class TokenModelProtocol(Protocol):
    token_hash: str
    username: str
    expires_at: datetime


class UserModelClassProtocol(Protocol):
    """Columns and constructor required from a user model class."""

    __tablename__: str
    metadata: MetaData
    __mapper__: Mapper[UserModelProtocol]

    @property
    def username_key(self) -> InstrumentedAttribute[str]: ...

    @property
    def email(self) -> InstrumentedAttribute[str]: ...

    def __call__(
        self,
        *,
        username: str,
        username_key: str,
        email: str,
        password_hash: str,
        verified: bool,
    ) -> UserModelProtocol: ...


class ModelBase:
    """SQLAlchemy's keyword constructor, shared by the model definitions."""

    __init__ = registry().constructor


class UserModel(ModelBase):
    __tablename__ = "userharbor_users"
    metadata: ClassVar[MetaData]
    __mapper__: ClassVar[Mapper[UserModelProtocol]]

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    username_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    @declared_attr
    def email_verifications(cls) -> Mapped[list["EmailVerificationModel"]]:
        return relationship("EmailVerificationModel", cascade="all, delete-orphan")

    @declared_attr
    def sessions(cls) -> Mapped[list["SessionModel"]]:
        return relationship("SessionModel", cascade="all, delete-orphan")

    @declared_attr
    def password_resets(cls) -> Mapped[list["PasswordResetModel"]]:
        return relationship("PasswordResetModel", cascade="all, delete-orphan")


class TokenModel(ModelBase):
    token_hash: Mapped[str] = mapped_column(
        String(128), primary_key=True, sort_order=-1
    )
    username: Mapped[str]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EmailVerificationModel(TokenModel):
    __tablename__ = "userharbor_email_verifications"


class SessionModel(TokenModel):
    __tablename__ = "userharbor_sessions"


class PasswordResetModel(TokenModel):
    __tablename__ = "userharbor_password_resets"


class RoleModel(ModelBase):
    __tablename__ = "userharbor_roles"
    role: Mapped[str] = mapped_column(String(255), primary_key=True)


class PermissionModel(ModelBase):
    __tablename__ = "userharbor_permissions"
    permission: Mapped[str] = mapped_column(String(255), primary_key=True)


class UserRoleModel(ModelBase):
    __tablename__ = "userharbor_user_roles"
    username: Mapped[str]
    role: Mapped[str] = mapped_column(
        ForeignKey("userharbor_roles.role", ondelete="CASCADE"), primary_key=True
    )


class RolePermissionModel(ModelBase):
    __tablename__ = "userharbor_role_permissions"
    role: Mapped[str] = mapped_column(
        ForeignKey("userharbor_roles.role", ondelete="CASCADE"), primary_key=True
    )
    permission: Mapped[str] = mapped_column(
        ForeignKey("userharbor_permissions.permission", ondelete="CASCADE"),
        primary_key=True,
    )


@dataclass(frozen=True)
class Models:
    Base: type[DeclarativeBase]
    UserModel: UserModelClassProtocol
    EmailVerificationModel: type[EmailVerificationModel]
    SessionModel: type[SessionModel]
    PasswordResetModel: type[PasswordResetModel]
    RoleModel: type[RoleModel]
    PermissionModel: type[PermissionModel]
    UserRoleModel: type[UserRoleModel]
    RolePermissionModel: type[RolePermissionModel]


ModelT = TypeVar("ModelT")


def _map_model(
    model: type[ModelT],
    base: type[DeclarativeBase],
    user_table: str | None = None,
    *,
    primary_key: bool = False,
) -> type[ModelT]:
    attributes = {"__module__": __name__}
    if user_table is not None:
        attributes["username"] = mapped_column(
            ForeignKey(f"{user_table}.username", ondelete="CASCADE"),
            nullable=False,
            primary_key=primary_key,
            index=not primary_key,
        )
    # The generated class inherits every typed field from the model definition.
    return cast(type[ModelT], type(model.__name__, (model, base), attributes))


def create_models(user_model: UserModelClassProtocol | None = None) -> Models:
    model_registry = registry(
        metadata=user_model.metadata if user_model is not None else None
    )
    base = type("UserHarborBase", (DeclarativeBase,), {"registry": model_registry})
    selected_user_model: UserModelClassProtocol = (
        user_model if user_model is not None else _map_model(UserModel, base)
    )
    user_table = selected_user_model.__tablename__
    return Models(
        Base=base,
        UserModel=selected_user_model,
        EmailVerificationModel=_map_model(EmailVerificationModel, base, user_table),
        SessionModel=_map_model(SessionModel, base, user_table),
        PasswordResetModel=_map_model(PasswordResetModel, base, user_table),
        RoleModel=_map_model(RoleModel, base),
        PermissionModel=_map_model(PermissionModel, base),
        UserRoleModel=_map_model(UserRoleModel, base, user_table, primary_key=True),
        RolePermissionModel=_map_model(RolePermissionModel, base),
    )
