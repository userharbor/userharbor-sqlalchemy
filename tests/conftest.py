from collections.abc import Callable, Iterator
from datetime import datetime

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.models import (
    EmailVerificationModel,
    PasswordResetModel,
    SessionModel,
    UserHarborBase,
    UserModel,
)
from userharbor_sqlalchemy.store import SQLAlchemyUserStore


@pytest.fixture
def engine() -> Iterator[Engine]:
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

    UserHarborBase.metadata.create_all(engine)
    try:
        yield engine
    finally:
        UserHarborBase.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


@pytest.fixture
def store(session_factory: sessionmaker[Session]) -> SQLAlchemyUserStore:
    return SQLAlchemyUserStore(session_factory)


@pytest.fixture
def expires_at() -> datetime:
    return datetime(2030, 1, 1, 12, 0, 0)


@pytest.fixture
def create_user_request(expires_at: datetime) -> CreateUserRequest:
    return CreateUserRequest(
        username="alice",
        email="alice@example.com",
        password_hash="password-hash",
        verification_token_hash="verification-token-hash",
        expires_at=expires_at,
    )


@pytest.fixture
def existing_user(
    store: SQLAlchemyUserStore,
    create_user_request: CreateUserRequest,
) -> CreateUserRequest:
    store.create_user(create_user_request)
    return create_user_request


@pytest.fixture
def read_session(session_factory: sessionmaker[Session]) -> Callable[[], Session]:
    def _read_session() -> Session:
        return session_factory()

    return _read_session


@pytest.fixture
def user_token(expires_at: datetime) -> UserToken:
    return UserToken(
        username="alice",
        token_hash="token-hash",
        expires_at=expires_at,
    )


def get_user(session: Session, username: str = "alice") -> UserModel | None:
    return session.get(UserModel, username)


def get_email_verification(
    session: Session,
    token_hash: str = "verification-token-hash",
) -> EmailVerificationModel | None:
    return session.get(EmailVerificationModel, token_hash)


def get_session_token(
    session: Session,
    token_hash: str = "token-hash",
) -> SessionModel | None:
    return session.get(SessionModel, token_hash)


def get_password_reset(
    session: Session,
    token_hash: str = "token-hash",
) -> PasswordResetModel | None:
    return session.get(PasswordResetModel, token_hash)


def list_sessions(session: Session, username: str = "alice") -> list[SessionModel]:
    return list(
        session.scalars(select(SessionModel).where(SessionModel.username == username))
    )
