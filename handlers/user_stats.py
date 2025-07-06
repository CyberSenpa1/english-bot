from aiogram import Router, types, F
from db.core import async_session
from db.models import user_statistics
from keyboards.user_kb import start_kb
from db.models import answer_logs, words
from sqlalchemy import select
from db.requests import get_problem_words
from datetime import datetime
from sqlalchemy import func
from aiogram.utils.markdown import hbold, hitalic
import logging



logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text.lower() == "статистика")
async def show_stats(message: types.Message):
    async with async_session() as session:
        try:
            # Получаем основную статистику
            stats_query = await session.execute(
                select(
                    user_statistics.c.learned_words,
                    user_statistics.c.total_words,
                    user_statistics.c.accuracy,
                    user_statistics.c.streak,
                    user_statistics.c.last_active,
                    func.coalesce(user_statistics.c.total_correct, 0).label("total_correct"),
                    func.coalesce(user_statistics.c.total_wrong, 0).label("total_wrong")
                )
                .where(user_statistics.c.user_id == message.from_user.id)
            )
            stats = stats_query.mappings().first()
            
            if not stats:
                await message.answer("📊 Статистика пока недоступна. Начните обучение!")
                return

            # Получаем проблемные слова (топ-5)
            problem_words = await get_problem_words(message.from_user.id, limit=5)
            
            # Получаем последние активности
            recent_activity = await session.execute(
                select(
                    answer_logs.c.timestamp,
                    answer_logs.c.is_correct,
                    words.c.english
                )
                .join(words, words.c.id == answer_logs.c.word_id)
                .where(answer_logs.c.user_id == message.from_user.id)
                .order_by(answer_logs.c.timestamp.desc())
                .limit(3)
            )
            
            # Формируем сообщение
            text = [
                hbold("📊 Ваша статистика"),
                "",
                f"🎯 {hitalic('Выучено слов:')} {stats.learned_words}/{stats.total_words}",
                f"📈 {hitalic('Точность:')} {stats.accuracy*100:.1f}% ({stats.total_correct}/{stats.total_correct + stats.total_wrong})",
                f"🔥 {hitalic('Серия дней:')} {stats.streak}",
                f"🔄 {hitalic('Последняя активность:')} {stats.last_active.strftime('%d.%m.%Y %H:%M')}",
                "",
                hbold("⚠️ Сложные слова:")
            ]
            
            if problem_words:
                for word in problem_words:
                    text.append(f"- {word['english']} ({word['wrong_attempts']} ошибок)")
            else:
                text.append("Пока нет сложных слов - отличная работа!")
            
            text.extend(["", hbold("⏱ Последние ответы:")])
            
            for activity in recent_activity:
                status = "✅" if activity.is_correct else "❌"
                text.append(f"{status} {activity.english} - {activity.timestamp.strftime('%H:%M')}")
            
            await message.answer("\n".join(text), parse_mode="HTML", reply_markup=start_kb)
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await message.answer(
                "Произошла ошибка при загрузке статистики. Попробуйте позже.",
                reply_markup=start_kb
            )