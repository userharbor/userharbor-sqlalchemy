from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy import select
from sqlalchemy.orm import Session
from userharbor.interfaces import CreateUserRequest, User, UserStore, UserToken

from .models import (
    EmailVerificationModel,
    PasswordResetModel,
    SessionModel,
    UserModel,
)

SessionFactory = Callable[[], Session]


class SQLAlchemyUserStore(UserStore):
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._current_session: ContextVar[Session | None] = ContextVar(
            "userharbor_current_session",
            default=None,
        )

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
                UserModel(
                    username=user.username,
                    email=user.email,
                    password_hash=user.password_hash,
                    verified=False,
                )
            )
            session.add(
                EmailVerificationModel(
                    username=user.username,
                    token_hash=user.verification_token_hash,
                    expires_at=user.expires_at,
                )
            )

    def set_user_verified(self, username: str) -> None:
        with self._session_scope() as session:
            user = session.get(UserModel, username)
            if user:
                user.verified = True

    def delete_user(self, username: str) -> None:
        with self._session_scope() as session:
            user = session.get(UserModel, username)
            if user:
                session.delete(user)

    def get_user_by_username(self, username: str) -> User | None:
        with self._session_scope() as session:
            user = session.get(UserModel, username)
            return _to_user(user) if user else None

    def get_user_by_email(self, email: str) -> User | None:
        with self._session_scope() as session:
            user = session.scalar(select(UserModel).where(UserModel.email == email))
            return _to_user(user) if user else None

    def get_email_verification(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            verification = session.get(EmailVerificationModel, token_hash)
            return _to_user_token(verification) if verification else None

    def set_email_verification(self, verification: UserToken) -> None:
        with self._session_scope() as session:
            session.add(
                EmailVerificationModel(
                    username=verification.username,
                    token_hash=verification.token_hash,
                    expires_at=verification.expires_at,
                )
            )

    def remove_email_verification(self, token_hash: str) -> None:
        with self._session_scope() as session:
            verification = session.get(EmailVerificationModel, token_hash)
            if verification:
                session.delete(verification)

    def get_session(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            user_session = session.get(SessionModel, token_hash)
            return _to_user_token(user_session) if user_session else None

    def add_session(self, session: UserToken) -> None:
        with self._session_scope() as _session:
            _session.add(
                SessionModel(
                    username=session.username,
                    token_hash=session.token_hash,
                    expires_at=session.expires_at,
                )
            )

    def remove_session(self, token_hash: str) -> None:
        with self._session_scope() as session:
            user_session = session.get(SessionModel, token_hash)
            if user_session:
                session.delete(user_session)

    def remove_all_sessions(self, username: str) -> None:
        with self._session_scope() as session:
            sessions = session.scalars(
                select(SessionModel).where(SessionModel.username == username)
            )
            for user_session in sessions:
                session.delete(user_session)

    def get_password_hash(self, username: str) -> str:
        with self._session_scope() as session:
            user = session.get(UserModel, username)
            if not user:
                raise KeyError(f"User not found: {username}")
            return user.password_hash

    def set_password_hash(self, username: str, password_hash: str) -> None:
        with self._session_scope() as session:
            user = session.get(UserModel, username)
            if not user:
                raise KeyError(f"User not found: {username}")
            user.password_hash = password_hash

    def get_password_reset(self, token_hash: str) -> UserToken | None:
        with self._session_scope() as session:
            reset = session.get(PasswordResetModel, token_hash)
            return _to_user_token(reset) if reset else None

    def set_password_reset(self, reset: UserToken) -> None:
        with self._session_scope() as session:
            session.add(
                PasswordResetModel(
                    username=reset.username,
                    token_hash=reset.token_hash,
                    expires_at=reset.expires_at,
                )
            )

    def remove_password_reset(self, token_hash: str) -> None:
        with self._session_scope() as session:
            reset = session.get(PasswordResetModel, token_hash)
            if reset:
                session.delete(reset)


def _to_user(model: UserModel) -> User:
    return User(
        username=model.username,
        email=model.email,
        verified=model.verified,
    )


def _to_user_token(
    model: EmailVerificationModel | SessionModel | PasswordResetModel,
) -> UserToken:
    return UserToken(
        username=model.username,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
    )
