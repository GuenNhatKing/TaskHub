import pytest_asyncio

from taskhub.core.security import hash_password
from taskhub.models import User

PASSWORD = "password@123"


@pytest_asyncio.fixture(scope="function")
async def active_user(db_session):
    user = User(
        full_name="Nhat King Active",
        email="test_user@mail.com",
        hashed_password=hash_password(PASSWORD),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {"email": user.email, "password": PASSWORD}
