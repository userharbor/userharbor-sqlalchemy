from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Callable, Generic, cast

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from sqlalchemy.schema import MetaData
from userharbor.interfaces import CreateUserRequest, UserStore, UserT, UserToken

from .mappers import default_user_mapper, token_mapper
from .models import UserModelProtocol, create_models

SessionFactory = Callable[[], Session]


class SQLAlchemyUserStore(UserStore[UserT], Generic[UserT]):
    def __init__(
        self,
        session_factory: SessionFactory,
        user_model: type[UserModelProtocol] | None = None,
        user_mapper: Callable[[UserModelProtocol], UserT] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._models = create_models(user_model)
        self._user_mapper = user_mapper or cast(
            Callable[[UserModelProtocol], UserT],
            default_user_mapper,
        )
        self._current_session: ContextVar[Session | None] = ContextVar(
            "userharbor_current_session",
            default=None,
        )

    @property
    def metadata(self) -> MetaData:
        return self._models.Base.metadata

    @contextmanager
    def transaction(self) -> Iterator[None]:
        existing_session = self._current_session.get()

        if existing_session is not None:
            yield
            return

        with self._session_factory() as session:
            token = self._current_session.set(session)
            try:
                with session.begin():
                    yield
            finally:
                self._current_session.reset(token)

    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        existing_session = self._current_session.get()

        if existing_session is not None:
            yield existing_session
            return

        with self._session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def create_user(self, user: CreateUserRequest) -> None:
        with self._session_scope() as session:
            session.add(
                self._models.UserModel(
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    verified=False,
                )
            )
            session.add(
                self._models.EmailVerificationModel(
                    username=user.username,
                    token_hash=user.verification_token_hash,
                    expires_at=user.expires_at,
                )
            )

    def set_user_verified(self, username: str) -> None:
        with self._session_scope() as session:
            user = session.get(self._models.UserModel, username)
            if user:
                user.verified = True

    def delete_user(self, username: str) -> None:
        with self._session_scope() as session:
            user = session.get(self._models.UserModel, username)
            if user:
                session.delete(user)

    def get_user_by_username(self, username: str) -> UserT | None:
        with self._session_scope() as session:
            user = session.get(self._models.UserModel, username)
            return self._user_mapper(user) if user else None

    def get_user_by_email(self, email: str) -> UserT | None:
        with self._session_scope() as session:
            user = session.scalar(
                select(self._models.UserModel).where(
                    self._models.UserModel.email == email
                )
            )
            return self._user_mapper(user) if user else None

    def get_email_verification(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            verification = session.get(self._models.EmailVerificationModel, token_hash)
            return token_mapper(verification) if verification else None

    def set_email_verification(self, verification: UserToken) -> None:
        with self._session_scope() as session:
            session.add(
                self._models.EmailVerificationModel(
                    username=verification.username,
                    token_hash=verification.token_hash,
                    expires_at=verification.expires_at,
                )
            )

    def remove_email_verification(self, token_hash: str) -> None:
        with self._session_scope() as session:
            verification = session.get(self._models.EmailVerificationModel, token_hash)
            if verification:
                session.delete(verification)

    def get_session(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            user_session = session.get(self._models.SessionModel, token_hash)
            return token_mapper(user_session) if user_session else None

    def add_session(self, session: UserToken) -> None:
        with self._session_scope() as _session:
            _session.add(
                self._models.SessionModel(
                    username=session.username,
                    token_hash=session.token_hash,
                    expires_at=session.expires_at,
                )
            )

    def remove_session(self, token_hash: str) -> None:
        with self._session_scope() as session:
            user_session = session.get(self._models.SessionModel, token_hash)
            if user_session:
                session.delete(user_session)

    def remove_all_sessions(self, username: str) -> None:
        with self._session_scope() as session:
            sessions = session.scalars(
                select(self._models.SessionModel).where(
                    self._models.SessionModel.username == username
                )
            )
            for user_session in sessions:
                session.delete(user_session)

    def refresh_session(self, token_hash: str, new_expires_at: datetime) -> None:
        with self._session_scope() as session:
            user_session = session.get(self._models.SessionModel, token_hash)
            if user_session:
                user_session.expires_at = new_expires_at

    def get_password_hash(self, username: str) -> str:
        with self._session_scope() as session:
            user = session.get(self._models.UserModel, username)
            if not user:
                raise KeyError(f"User not found: {username}")
            return user.password_hash

    def set_password_hash(self, username: str, password_hash: str) -> None:
        with self._session_scope() as session:
            user = session.get(self._models.UserModel, username)
            if not user:
                raise KeyError(f"User not found: {username}")
            user.password_hash = password_hash

    def get_password_reset(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            reset = session.get(self._models.PasswordResetModel, token_hash)
            return token_mapper(reset) if reset else None

    def set_password_reset(self, reset: UserToken) -> None:
        with self._session_scope() as session:
            session.add(
                self._models.PasswordResetModel(
                    username=reset.username,
                    token_hash=reset.token_hash,
                    expires_at=reset.expires_at,
                )
            )

    def remove_password_reset(self, token_hash: str) -> None:
        with self._session_scope() as session:
            reset = session.get(self._models.PasswordResetModel, token_hash)
            if reset:
                session.delete(reset)

    def create_role(self, role: str) -> None:
        with self._session_scope() as session:
            session.add(self._models.RoleModel(role=role))

    def delete_role(self, role: str) -> None:
        with self._session_scope() as session:
            session.execute(
                delete(self._models.UserRoleModel).where(
                    self._models.UserRoleModel.role == role
                )
            )
            session.execute(
                delete(self._models.RolePermissionModel).where(
                    self._models.RolePermissionModel.role == role
                )
            )
            role_model = session.get(self._models.RoleModel, role)
            if role_model:
                session.delete(role_model)

    def list_roles(self) -> set[str]:
        with self._session_scope() as session:
            return set(session.scalars(select(self._models.RoleModel.role)))

    def role_exists(self, role: str) -> bool:
        with self._session_scope() as session:
            return session.get(self._models.RoleModel, role) is not None

    def grant_role_to_user(self, username: str, role: str) -> None:
        with self._session_scope() as session:
            user_role = session.get(self._models.UserRoleModel, (username, role))
            if not user_role:
                session.add(self._models.UserRoleModel(username=username, role=role))

    def revoke_role_from_user(self, username: str, role: str) -> None:
        with self._session_scope() as session:
            user_role = session.get(self._models.UserRoleModel, (username, role))
            if user_role:
                session.delete(user_role)

    def get_user_roles(self, username: str) -> set[str]:
        with self._session_scope() as session:
            return set(
                session.scalars(
                    select(self._models.UserRoleModel.role).where(
                        self._models.UserRoleModel.username == username
                    )
                )
            )

    def create_permission(self, permission: str) -> None:
        with self._session_scope() as session:
            session.add(self._models.PermissionModel(permission=permission))

    def delete_permission(self, permission: str) -> None:
        with self._session_scope() as session:
            session.execute(
                delete(self._models.RolePermissionModel).where(
                    self._models.RolePermissionModel.permission == permission
                )
            )
            permission_model = session.get(self._models.PermissionModel, permission)
            if permission_model:
                session.delete(permission_model)

    def list_permissions(self) -> set[str]:
        with self._session_scope() as session:
            return set(session.scalars(select(self._models.PermissionModel.permission)))

    def permission_exists(self, permission: str) -> bool:
        with self._session_scope() as session:
            return session.get(self._models.PermissionModel, permission) is not None

    def grant_permission_to_role(self, role: str, permission: str) -> None:
        with self._session_scope() as session:
            role_permission = session.get(
                self._models.RolePermissionModel,
                (role, permission),
            )
            if not role_permission:
                session.add(
                    self._models.RolePermissionModel(
                        role=role,
                        permission=permission,
                    )
                )

    def revoke_permission_from_role(self, role: str, permission: str) -> None:
        with self._session_scope() as session:
            role_permission = session.get(
                self._models.RolePermissionModel,
                (role, permission),
            )
            if role_permission:
                session.delete(role_permission)

    def get_role_permissions(self, role: str) -> set[str]:
        with self._session_scope() as session:
            return set(
                session.scalars(
                    select(self._models.RolePermissionModel.permission).where(
                        self._models.RolePermissionModel.role == role
                    )
                )
            )

    def get_user_permissions(self, username: str) -> set[str]:
        with self._session_scope() as session:
            return set(
                session.scalars(
                    select(self._models.RolePermissionModel.permission)
                    .join(
                        self._models.UserRoleModel,
                        self._models.UserRoleModel.role
                        == self._models.RolePermissionModel.role,
                    )
                    .where(self._models.UserRoleModel.username == username)
                )
            )
