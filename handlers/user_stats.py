from aiogram import Router, types, F
from db.core import async_session
from db.models import user_statistics
from keyboards.user_kb import start_kb
from db.models import answer_logs
from sqlalchemy import select
from db.requests import get_problem_words

router = Router()

@router.message(F.text.lower() == "статистика")
async def show_stats(message: types.Message):
    async with async_session() as session:
        try:
            # Основная статистика
            stats = await session.execute(
                select(user_statistics)
                .where(user_statistics.c.user_id == message.from_user.id)
            )
            stats = stats.mappings().one_or_none()
            
            # Проблемные слова
            problem_words = await get_problem_words(message.from_user.id)
            
            # Формируем сообщение
            text = (
                f"📊 <b>Ваша статистика</b>\n\n"
                f"🎯 Выучено слов: {stats['learned_words']}/{stats['total_words']}\n"
                f"📈 Точность: {stats['accuracy']*100:.1f}%\n"
                f"🔥 Серия дней: {stats['streak']}\n\n"
                f"🔄 Последняя активность: {stats['last_active'].strftime('%d.%m.%Y')}\n\n"
                f"⚠️ <b>Сложные слова:</b>\n"
            )
            
            for word in problem_words:
                text += f"- {word['english']} ({word['wrong_attempts']} ошибок)\n"
        except:
            await message.answer("Пока нету статистики")
        
        await message.answer(text, parse_mode="HTML")