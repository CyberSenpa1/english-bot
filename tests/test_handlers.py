import pytest
from db.core import async_session
from db.crud import add_user, get_user
from db.models import users

@pytest.mark.asyncio
async def test_add_and_get_user():
    async with async_session() as session:
        # Удаляем пользователя, если он есть
        await session.execute(users.delete().where(users.c.user_id == 123))
        await session.commit()

        await add_user(session, 123, "testuser", "Test")
        user = await get_user(session, 123)
        assert user is not None
        assert user["user_id"] == 123

        # Можно также удалить пользователя после теста
        await session.execute(users.delete().where(users.c.user_id == 123))
        await session.commit()