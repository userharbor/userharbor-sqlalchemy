from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from userharbor_sqlalchemy.store import SQLAlchemyUserStore


@pytest.fixture
def store() -> Iterator[SQLAlchemyUserStore]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    user_store = SQLAlchemyUserStore(sessionmaker(bind=engine))
    user_store.metadata.create_all(engine)

    try:
        yield user_store
    finally:
        user_store.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def user_store(store: SQLAlchemyUserStore) -> SQLAlchemyUserStore:
    return store


@pytest.fixture
def session(store: SQLAlchemyUserStore) -> Iterator[Session]:
    with store._session_factory() as session:
        yield session
