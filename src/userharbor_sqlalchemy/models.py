from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class UserHarborBase(DeclarativeBase):
    pass


class UserModel(UserHarborBase):
    __tablename__ = "userharbor_users"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    email_verifications: Mapped[list["EmailVerificationModel"]] = relationship(
        cascade="all, delete-orphan"
    )
    sessions: Mapped[list["SessionModel"]] = relationship(cascade="all, delete-orphan")
    password_resets: Mapped[list["PasswordResetModel"]] = relationship(
        cascade="all, delete-orphan"
    )


class EmailVerificationModel(UserHarborBase):
    __tablename__ = "userharbor_email_verifications"

    token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
    username: Mapped[str] = mapped_column(
        ForeignKey("userharbor_users.username", ondelete="CASCADE"),
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SessionModel(UserHarborBase):
    __tablename__ = "userharbor_sessions"

    token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
    username: Mapped[str] = mapped_column(
        ForeignKey("userharbor_users.username", ondelete="CASCADE"),
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PasswordResetModel(UserHarborBase):
    __tablename__ = "userharbor_password_resets"

    token_hash: Mapped[str] = mapped_column(String(128), primary_key=True)
    username: Mapped[str] = mapped_column(
        ForeignKey("userharbor_users.username", ondelete="CASCADE"),
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
