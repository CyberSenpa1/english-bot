from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import users
from datetime import datetime

async def get_user(session: AsyncSession, user_id: int):
    """Получить пользователя по user_id."""
    result = await session.execute(select(users).where(users.c.user_id == user_id))
    return result.mappings().first()

async def add_user(session: AsyncSession, user_id: int, username: str, first_name: str):
    """Добавить нового пользователя."""
    new_user = users.insert().values(
        user_id=user_id,
        username=username,
        first_name=first_name,
        reg_date=datetime.now()
    )
    await session.execute(new_user)
    await session.commit()

async def update_user(session: AsyncSession, user_id: int, username: str = None, first_name: str = None):
    """Обновить информацию о пользователе."""
    stmt = update(users).where(users.c.user_id == user_id)
    if username:
        stmt = stmt.values(username=username)
    if first_name:
        stmt = stmt.values(first_name=first_name)
    await session.execute(stmt)
    await session.commit()

async def delete_user(session: AsyncSession, user_id: int):
    """Удалить пользователя."""
    stmt = delete(users).where(users.c.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
