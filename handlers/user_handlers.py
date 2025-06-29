from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from db.core import async_session
from db.crud import get_user, add_user, update_user
from db.models import users
from keyboards.user_kb import start_kb


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    async with async_session() as session:
        existing_user = await get_user(session, user_id)
        if existing_user is None:
            await add_user(session, user_id, username, first_name)
            await message.answer("Добро пожаловать! Вы успешно зарегистрированы.", reply_markup=start_kb)
        else:
            await message.answer("Вы уже зарегистрированы. Добро пожаловать обратно!", reply_markup=start_kb)
    await state.clear()

