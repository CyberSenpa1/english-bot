from db.models import answer_logs, user_words, user_statistics, words
from sqlalchemy import select, func, insert, update
from db.core import async_session
from datetime import datetime, timedelta
from db.models import users

async def log_answer(
    user_id: int,
    word_id: int,
    is_correct: bool,
    mode: str,
    response_time: float,
    session_id: int = None
):
    try:

        async with async_session() as session:
            user_exists = await session.execute(
            select(1).where(users.c.user_id == user_id)
        )
            if not user_exists.scalar():
                await session.execute(
                    insert(users)
                    .values(id=user_id)
                    .on_conflict_do_nothing(index_elements=['id'])
                )


            stmt = answer_logs.insert().values(
                user_id=user_id,
                word_id=word_id,
                session_id=session_id,
                is_correct=is_correct,
                mode=mode,
                response_time=response_time
            )
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        print(e)


async def update_word_progress(
    user_id: int,
    word_id: int,
    is_correct: bool
):
    async with async_session() as session:
        # Получаем текущий прогресс
        result = await session.execute(
            select(user_words)
            .where(
                (user_words.c.user_id == user_id) &
                (user_words.c.word_id == word_id)
            )
        )
        progress = result.mappings().one_or_none()
        
        if not progress:
            # Инициализация для нового слова
            stmt = user_words.insert().values(
                user_id=user_id,
                word_id=word_id,
                correct_attempts=1 if is_correct else 0,
                wrong_attempts=0 if is_correct else 1,
                last_reviewed=func.now(),
                next_review=func.now() + timedelta(days=1),  # Исправлено здесь
                ease_factor=2.5
            )
        else:
            # Алгоритм SM-2 (модифицированный для SRS)
            if is_correct:
                new_repetitions = progress["repetitions"] + 1
                ease_factor = max(1.3, progress["ease_factor"] + 0.1)
                
                if new_repetitions == 1:
                    interval = 1
                elif new_repetitions == 2:
                    interval = 6
                else:
                    interval = round(progress["interval"] * ease_factor)
            else:
                new_repetitions = 0
                ease_factor = max(1.3, progress["ease_factor"] - 0.15)
                interval = 1
            
            stmt = user_words.update()\
                .where(
                    (user_words.c.user_id == user_id) &
                    (user_words.c.word_id == word_id)
                )\
                .values(
                    repetitions=new_repetitions,
                    interval=interval,
                    ease_factor=ease_factor,
                    last_reviewed=func.now(),
                    next_review=func.now() + timedelta(days=interval),  # И здесь исправлено
                    correct_attempts=progress["correct_attempts"] + (1 if is_correct else 0),
                    wrong_attempts=progress["wrong_attempts"] + (0 if is_correct else 1),
                    is_learning=(new_repetitions < 5)
                )
        
        await session.execute(stmt)
        await session.commit()


async def update_user_stats(user_id: int):
    async with async_session() as session:
        # Получаем статистические данные
        total_words = await session.scalar(select(func.count(words.c.id)))
        learned_words = await session.scalar(
            select(func.count(user_words.c.word_id))
            .where(
                (user_words.c.user_id == user_id) & 
                (user_words.c.is_learning == False)
            )
        )
        total_correct = await session.scalar(
            select(func.sum(user_words.c.correct_attempts))
            .where(user_words.c.user_id == user_id)
        ) or 0
        total_wrong = await session.scalar(
            select(func.sum(user_words.c.wrong_attempts))
            .where(user_words.c.user_id == user_id)
        ) or 0

        # Проверяем существование записи
        exists = await session.scalar(
            select(user_statistics.c.id)
            .where(user_statistics.c.user_id == user_id)
        )

        if exists:
            # Обновляем существующую запись
            stmt = update(user_statistics)\
                .where(user_statistics.c.user_id == user_id)\
                .values(
                    learned_words=learned_words,
                    total_correct=total_correct,
                    total_wrong=total_wrong,
                    last_active=func.now()
                )
        else:
            # Создаем новую запись
            stmt = insert(user_statistics)\
                .values(
                    user_id=user_id,
                    total_words=total_words,
                    learned_words=learned_words,
                    total_correct=total_correct,
                    total_wrong=total_wrong,
                    last_active=func.now()
                )
        
        await session.execute(stmt)
        await session.commit()

async def get_problem_words(user_id: int, limit: int = 5):
    async with async_session() as session:
        result = await session.execute(
            select(
                words.c.english,
                words.c.russian,
                user_words.c.wrong_attempts
            )
            .join(user_words, user_words.c.word_id == words.c.id)
            .where(
                (user_words.c.user_id == user_id) &
                (user_words.c.wrong_attempts > 0)
            )
            .order_by(user_words.c.wrong_attempts.desc())
            .limit(limit)
        )
        return result.mappings().all()
    
async def remove_difficult_words(user_id: int, word_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            user_words.delete().where(
                (user_words.c.user_id == user_id) & 
                (user_words.c.word_id == word_id) &
                (user_words.c.wrong_attempts > 5)
            )
        )
        await session.commit()
        return result.rowcount  # возвращаем количество удаленных строк