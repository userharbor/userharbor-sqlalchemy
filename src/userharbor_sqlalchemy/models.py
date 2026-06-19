from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class UserModelProtocol(Protocol):
    username: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]
    verified: Mapped[bool]


class TokenModelProtocol(Protocol):
    token_hash: Mapped[str]
    username: Mapped[str]
    expires_at: Mapped[datetime]


@dataclass(frozen=True)
class Models:
    Base: type[DeclarativeBase]
    UserModel: type[UserModelProtocol]
    EmailVerificationModel: type[TokenModelProtocol]
    SessionModel: type[TokenModelProtocol]
    PasswordResetModel: type[TokenModelProtocol]


def create_models(user_model: type[UserModelProtocol] | None = None) -> Models:
    class UserHarborBase(DeclarativeBase):
        pass

    if not user_model:

        class UserModel(UserHarborBase):
            __tablename__ = "userharbor_users"

            username: Mapped[str] = mapped_column(String(255), primary_key=True)
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

    return Models(
        Base=UserHarborBase,
        UserModel=user_model,
        EmailVerificationModel=EmailVerificationModel,
        SessionModel=SessionModel,
        PasswordResetModel=PasswordResetModel,
    )
