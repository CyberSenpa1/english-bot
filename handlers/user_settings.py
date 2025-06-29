from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.core import async_session
from db.models import srs_settings

router = Router()

class SettingsState(StatesGroup):
    waiting_for_setting = State()

@router.message(lambda m: m.text == "Сложность")
async def ask_difficulty(message: types.Message, state: FSMContext):
    await message.answer("Выберите уровень сложности (1-5):")
    await state.set_state(SettingsState.waiting_for_setting)

@router.message(SettingsState.waiting_for_setting)
async def set_difficulty(message: types.Message, state: FSMContext):
    try:
        level = int(message.text)
        if not 1 <= level <= 5:
            raise ValueError
    except ValueError:
        await message.answer("Введите число от 1 до 5.")
        return
    async with async_session() as session:
        await session.execute(
            srs_settings.update()
            .where(srs_settings.c.user_id == message.from_user.id)
            .values(initial_easy_factor=level)
        )
        await session.commit()
    await message.answer(f"Сложность установлена на {level}")
    await state.clear()