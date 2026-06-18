# UserHarbor SQLAlchemy

> **Project status:** UserHarbor SQLAlchemy is currently in an early stage of development.
> The API may change frequently. The library is not ready for production use yet.

`userharbor-sqlalchemy` provides a SQLAlchemy-based `UserStore` implementation for
[`userharbor`](https://github.com/userharbor/userharbor).

It stores:

* users,
* email verification tokens,
* sessions,
* password reset tokens,
* password hashes.

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
from userharbor_sqlalchemy.models import UserHarborBase


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


engine = create_engine("sqlite:///users.db")
SessionLocal = sessionmaker(bind=engine)

UserHarborBase.metadata.create_all(engine)

store = SQLAlchemyUserStore(SessionLocal)
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

harbor.logout(session_token)
```

For real applications, replace `EmailSender` with an implementation that sends
verification and password reset messages through your email provider.

---

## Transactions

`SQLAlchemyUserStore.transaction()` provides a transaction context used by
UserHarbor for multi-step operations such as email verification, password reset,
password change, and account deletion. Successful blocks are committed; exceptions
roll back all changes from the block.

---

## License

UserHarbor SQLAlchemy is released under the MIT License.
