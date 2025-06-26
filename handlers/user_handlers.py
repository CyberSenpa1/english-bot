from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from db.core import async_session
from db.crud import get_user, add_user, update_user
from db.models import users


router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    async with async_session() as session:
        existing_user = await get_user(session, user_id)
        if existing_user is None:
            await add_user(session, user_id, username, first_name)
            await message.answer("Добро пожаловать! Вы успешно зарегистрированы.")
        else:
            await message.answer("Вы уже зарегистрированы. Добро пожаловать обратно!")
    await state.clear()
