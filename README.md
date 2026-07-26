<picture>
  <img src="https://github.com/userharbor/userharbor/raw/master/docs/assets/logo-full.png" alt="userharbor">
</picture>

[![GitHub License](https://img.shields.io/github/license/userharbor/userharbor-sqlalchemy)](https://github.com/userharbor/userharbor-sqlalchemy?tab=MIT-1-ov-file)
[![Tests](https://img.shields.io/github/actions/workflow/status/userharbor/userharbor-sqlalchemy/publish.yml?label=tests)](https://github.com/userharbor/userharbor-sqlalchemy/blob/master/.github/workflows/tests.yml)
[![Codecov](https://img.shields.io/codecov/c/github/userharbor/userharbor-sqlalchemy)](https://codecov.io/gh/userharbor/userharbor-sqlalchemy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/userharbor-sqlalchemy)](https://pypi.org/project/userharbor-sqlalchemy)
[![PyPI - Version](https://img.shields.io/pypi/v/userharbor-sqlalchemy)](https://pypi.org/project/userharbor-sqlalchemy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-Ruff-black?logo=ruff&logoColor=black)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pytest](https://img.shields.io/badge/testing-Pytest-red?logo=pytest&logoColor=red)](https://docs.pytest.org/)
[![Zensical](https://img.shields.io/badge/docs-Zensical-yellow?logo=MaterialForMkDocs&logoColor=yellow)](https://userharborpaceshaman.github.io/userharbor/)

> **Project status:** UserHarbor SQLAlchemy is currently in an early stage of development.
> The API may change frequently. The library is not ready for production use yet.

`userharbor-sqlalchemy` provides a SQLAlchemy-based `UserStore` implementation for
[`userharbor`](https://github.com/userharbor/userharbor-sqlalchemy).

It stores:

* users
* email verification tokens
* sessions
* password reset tokens
* password hashes
* roles
* permissions
* user-to-role assignments
* role-to-permission assignments

Each user has at most one active email verification token and one active
password reset token. Storing a new token of either kind removes that user's
previous token. Users can have multiple active sessions.

The package only handles persistence. It does not send emails, expose HTTP endpoints,
or implement application-specific authentication flows.

---

## Installation

```bash
pip install userharbor-sqlalchemy
```

This package depends on `userharbor` and SQLAlchemy 2.x.

---

## Example usage

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from userharbor import UserHarbor
from userharbor_sqlalchemy import SQLAlchemyUserStore


class EmailSender:
    def send_verification(
        self,
        username: str,
        email: str,
        verification_token: str,
    ) -> None:
        print(f"Send verification token to {email}: {verification_token}")

    def send_password_reset(
        self,
        username: str,
        email: str,
        reset_token: str,
    ) -> None:
        print(f"Send password reset token to {email}: {reset_token}")

    def send_email_verified(self, username: str, email: str) -> None:
        print(f"Email verified for {email}")

    def send_password_changed(self, username: str, email: str) -> None:
        print(f"Password changed for {email}")

    def send_account_deleted(self, username: str, email: str) -> None:
        print(f"Account deleted for {email}")


engine = create_engine("sqlite:///users.db")
SessionLocal = sessionmaker(bind=engine)

store = SQLAlchemyUserStore(SessionLocal)
store.metadata.create_all(engine)
email_sender = EmailSender()

harbor = UserHarbor(
    secret_key="your-secret-key",
    store=store,
    email_sender=email_sender,
)

harbor.register(
    username="jane",
    email="jane@example.com",
    password="StrongPassword123!",
)

harbor.verify_email("verification-token-from-email")

session_token = harbor.login(
    username="jane",
    password="StrongPassword123!",
)

current_user = harbor.get_current_user(session_token)
print(current_user.username)

harbor.roles.create("admin")
harbor.permissions.create("users.delete")
harbor.roles.grant_permission("admin", "users.delete")
harbor.grant_role("jane", "admin")

if harbor.has_permission(session_token, "users.delete"):
    print("User can delete users")

harbor.logout(session_token)
```

For real applications, replace `EmailSender` with an implementation that sends
verification and password reset messages through your email provider.

---

## Transactions

`SQLAlchemyUserStore.transaction()` provides a transaction context used by
UserHarbor for multi-step operations such as email verification, password reset,
password change, account deletion, and role or permission assignment. Successful
blocks are committed; exceptions roll back all changes from the block.

---

## License

UserHarbor SQLAlchemy is released under the MIT License.
