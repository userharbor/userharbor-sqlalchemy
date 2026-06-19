from userharbor.interfaces import User, UserToken

from .models import TokenModelProtocol, UserModelProtocol


def default_user_mapper(model: UserModelProtocol) -> User:
    return User(
        username=model.username,
        email=model.email,
        verified=model.verified,
    )


def token_mapper(model: TokenModelProtocol) -> UserToken:
    return UserToken(
        username=model.username,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
    )
