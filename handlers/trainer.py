from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db.core import async_session
from db.models import words, user_words
import random
from redis.asyncio import Redis
from keyboards.user_kb import get_trainer_keyboard, start_kb
import asyncio
from datetime import datetime
from db.requests import log_answer, update_user_stats, update_word_progress, remove_difficult_words
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()

class TrainerState(StatesGroup):
    waiting_for_answer = State()

async def get_words_for_user(user_id, session, limit=10):
    # Получить слова, которые пользователь чаще всего ошибается или давно не повторял
    result = await session.execute(
        user_words.select()
        .where(user_words.c.user_id == user_id)
        .order_by(user_words.c.wrong_attempts.desc(), user_words.c.next_review.asc())
        .limit(limit)
    )
    user_word_rows = result.fetchall()
    word_ids = [row.word_id for row in user_word_rows]
    words_list = []
    if word_ids:
        result = await session.execute(words.select().where(words.c.id.in_(word_ids)))
        words_list = list(result.fetchall())
    # Если после фильтрации меньше 3 слов — добираем случайные из всех
    if len(words_list) < 3:
        result = await session.execute(words.select())
        all_words = list(result.fetchall())
        # Добавляем недостающие слова, которых ещё нет в words_list
        extra = [w for w in all_words if w.id not in word_ids]
        random.shuffle(extra)
        words_list += extra[:max(0, 3 - len(words_list))]
    return words_list


@router.message(F.text.lower() == "изучение английского")
async def start_training(message: types.Message, state: FSMContext, redis):
    await redis.set("test", "value")
    async with async_session() as session:
        word_rows = await get_words_for_user(message.from_user.id, session)
    if len(word_rows) < 3:
        await message.answer("Недостаточно слов для тренировки.")
        return
    chosen = random.sample(word_rows, 3)
    correct = random.choice(chosen)
    options = [w.russian for w in chosen]
    random.shuffle(options)
    await state.set_state(TrainerState.waiting_for_answer)
    await state.update_data(correct_word_id=correct.id, correct_russian=correct.russian)
    # Сохраняем в Redis текущий вопрос (можно для статистики)
    await redis.set(f"user:{message.from_user.id}:current_word", correct.id)

    await message.answer(
        f"Как переводится слово: <b>{correct.english}</b>?",
        reply_markup=get_trainer_keyboard(options),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_menu", TrainerState.waiting_for_answer)
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=start_kb)
    await callback.answer()


@router.callback_query(TrainerState.waiting_for_answer)
async def check_answer(callback: types.CallbackQuery, state: FSMContext, redis: Redis):
    start_time = datetime.now()
    
    data = await state.get_data()
    correct_russian = data.get("correct_russian")
    word_id = data.get("correct_word_id")
    session_id = data.get("session_id")
    user_id = callback.from_user.id
    
    is_correct = callback.data == correct_russian
    
    # Логируем ответ
    response_time = (datetime.now() - start_time).total_seconds()
    await log_answer(
        user_id=user_id,
        word_id=word_id,
        is_correct=is_correct,
        mode="quiz",
        response_time=response_time,
        session_id=session_id
    )
    
    async with async_session() as session:
        # Получаем правильное слово из базы для отображения
        result = await session.execute(words.select().where(words.c.id == word_id))
        correct_word = result.fetchone()
        
        # Обновляем статистику
        result = await session.execute(
            user_words.select().where(
                (user_words.c.user_id == user_id) & (user_words.c.word_id == word_id)
            )
        )
        user_word = result.fetchone()
        
        if user_word:
            new_wrong_attempts = user_word.wrong_attempts + (0 if is_correct else 1)
            upd = user_words.update().where(
                (user_words.c.user_id == user_id) & (user_words.c.word_id == word_id)
            ).values(
                correct_attempts=user_word.correct_attempts + (1 if is_correct else 0),
                wrong_attempts=new_wrong_attempts
            )
            await session.execute(upd)
        else:
            new_wrong_attempts = 0 if is_correct else 1
            ins = user_words.insert().values(
                user_id=user_id,
                word_id=word_id,
                correct_attempts=1 if is_correct else 0,
                wrong_attempts=new_wrong_attempts
            )
            await session.execute(ins)
        
        await session.commit()
        
        # Проверяем и удаляем сложные слова после коммита
        if new_wrong_attempts > 3:  # порог для удаления
            removed_count = await remove_difficult_words(user_id, word_id)
            if removed_count:
                await callback.message.answer(
                    f"🗑 Слово <b>{correct_word.english}</b> было удалено из вашего словаря, "
                    "так как вызвало много ошибок. Вы можете добавить его снова позже.",
                    parse_mode="HTML"
                )
    
    try:
        await callback.message.delete()
    except:
        pass

    if is_correct:
        msg = await callback.message.answer(
            "✅ <b>Правильно!</b>\n"
            f"<code>{correct_word.english}</code> = {correct_word.russian}",
            parse_mode="HTML"
        )
    else:
        msg = await callback.message.answer(
            "❌ <b>Ошибка!</b>\n"
            f"Вы выбрали: <s>{callback.data}</s>\n"
            f"Правильный ответ: <code>{correct_word.english}</code> = {correct_word.russian}",
            parse_mode="HTML"
        )
    
    await callback.answer()
    await start_training(callback.message, state, redis)