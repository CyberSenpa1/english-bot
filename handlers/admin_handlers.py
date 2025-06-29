from aiogram import types, Router, Bot
from aiogram.filters import Command, Filter
from aiogram.enums import ParseMode
from admins import admins_id

router = Router()


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in admins_id.values()

@router.message(Command("admin"), IsAdmin())
async def admin_start(message: types.Message):
    """
    Обработчик команды /start для администраторов.
    Отправляет приветственное сообщение и список доступных команд.
    """
    if message.from_user.id not in admins_id.values():
        None  # Игнорируем команды от неадминистраторов
        return
    else:
        await message.answer(
            "Привет, админ! 👋\n"
            "Я бот для изучения английского языка. Вот список доступных команд:\n"
            "/add_word - Добавить новое слово\n"
            "/remove_word - Удалить слово\n"
            "/view_stats - Просмотреть статистику пользователей\n",
            parse_mode=ParseMode.HTML
        )

async def notify_admins_on_start(bot: Bot):
    """
    Отправляет всем администраторам сообщение о запуске бота.
    """
    for admin_id in admins_id.values():
        try:
            await bot.send_message(
                admin_id,
                "Бот успешно запущен и готов к работе! 🚀"
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение админу {admin_id}: {e}")