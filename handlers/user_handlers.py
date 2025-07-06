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

@router.message(F.text.lower() == "о нас")
async def cmd_about_us(message: Message):
    await message.answer("Ссылка на проект:https://github.com/CyberSenpa1/english-bot")

@router.message(F.text.lower() == "поддержать автора")
async def support_author(message: Message):
    await message.answer(f"<b>BTC</b>:<u><code>1Nyu72SD2iHVh7a1W36cWpufoF2GJYGvfZ</code></u>\n"
                          f"<b>TON</b>:<u><code>UQAEMK1JJFmCe4ZEGsoX_cjGuRztDn7y63DPo_-bU5uHseBg</code></u>", parse_mode="HTML")
    


