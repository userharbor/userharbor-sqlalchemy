from datetime import datetime, timezone

from userharbor.interfaces import CreateUserRequest, UserToken

from userharbor_sqlalchemy.models import create_models
from userharbor_sqlalchemy.store import SQLAlchemyUserStore


def test_model_factories_keep_metadata_and_relationships_isolated() -> None:
    first = create_models()
    second = create_models()

    assert first.Base.metadata is not second.Base.metadata
    assert first.UserModel is not second.UserModel
    assert first.SessionModel is not second.SessionModel
    assert (
        first.UserModel.__mapper__.registry is not second.UserModel.__mapper__.registry
    )
    assert (
        first.UserModel.__mapper__.relationships["sessions"].mapper.class_
        is first.SessionModel
    )
    assert (
        second.UserModel.__mapper__.relationships["sessions"].mapper.class_
        is second.SessionModel
    )


def test_default_model_relationships_still_delete_tokens(
    store: SQLAlchemyUserStore,
) -> None:
    expires_at = datetime(2030, 1, 1, tzinfo=timezone.utc)
    store.create_user(
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            password_hash="password-hash",
            verification_token_hash="verification-hash",
            expires_at=expires_at,
        )
    )
    store.add_session(UserToken("alice", "session-hash", expires_at))
    store.set_password_reset(UserToken("alice", "reset-hash", expires_at))

    with store._session_factory() as session:
        user = session.get(store._models.UserModel.__mapper__, "alice")
        assert user is not None
        session.delete(user)
        session.commit()

    assert store.get_email_verification("verification-hash") is None
    assert store.get_session("session-hash") is None
    assert store.get_password_reset("reset-hash") is None


def test_user_foreign_keys_are_required_and_cascade_deletions() -> None:
    models = create_models()
    for model in (
        models.EmailVerificationModel,
        models.SessionModel,
        models.PasswordResetModel,
        models.UserRoleModel,
    ):
        column = model.username.property.columns[0]
        assert not column.nullable
        foreign_key = next(iter(column.foreign_keys))
        assert foreign_key.target_fullname == "userharbor_users.username"
        assert foreign_key.ondelete == "CASCADE"
