from userharbor_sqlalchemy import SQLAlchemyUserStore
from userharbor_sqlalchemy.store import SQLAlchemyUserStore as StoreImplementation


def test_exports_sqlalchemy_user_store() -> None:
    assert SQLAlchemyUserStore is StoreImplementation
