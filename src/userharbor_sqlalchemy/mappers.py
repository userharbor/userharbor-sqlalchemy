from dataclasses import dataclass

from userharbor.interfaces import UserToken

from .models import TokenModelProtocol, UserModelProtocol


@dataclass(frozen=True)
class User:
    username: str
    email: str
    verified: bool


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
