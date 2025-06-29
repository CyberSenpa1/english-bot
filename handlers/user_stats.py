from aiogram import Router, types
from db.core import async_session
from db.models import user_statistics

router = Router()

@router.message(lambda m: m.text == "Статистика")
async def show_stats(message: types.Message):
    async with async_session() as session:
        result = await session.execute(
            user_statistics.select().where(user_statistics.c.user_id == message.from_user.id)
        )
        stats = result.scalar_one_or_none()
    if not stats:
        await message.answer("Статистика пока не доступна.")
        return
    await message.answer(
        f"Выучено слов: {stats.learned_words}\n"
        f"Всего слов: {stats.total_words}\n"
        f"Текущий стрик: {stats.streak}\n"
        f"Точность: {round(stats.accuracy * 100, 2) if stats.accuracy else 0}%"
    )