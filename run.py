import os
import asyncio
import logging
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from handlers import user_handlers, admin_handlers
from handlers.admin_handlers import notify_admins_on_start
from db.core import init_db, get_redis, close_redis

from os import getenv

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


async def on_startup(dispatcher: Dispatcher):
    """Действия при запуске бота"""
    try:
        await init_db()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}", exc_info=True)
        raise

async def on_shutdown(dispatcher: Dispatcher):
    """Действия при остановке бота"""
    try:
        await dispatcher.emit_shutdown()
        await close_redis()
        logger.info("Ресурсы успешно освобождены")
    except Exception as e:
        logger.error(f"Ошибка при остановке: {e}")
    finally:
        logger.info("Бот остановлен")

@asynccontextmanager
async def lifespan(dispatcher: Dispatcher):
    await on_startup(dispatcher)
    yield
    await on_shutdown(dispatcher)

async def main():
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("База данных инициализирована")

        # Инициализация бота
        bot = Bot(token=getenv("BOT_TOKEN"))

        await notify_admins_on_start(bot)

        # Инициализация хранилища FSM
        redis = await get_redis()
        storage = RedisStorage(redis)

        # Создание диспетчера
        dp = Dispatcher(storage=storage)
        dp.include_router(admin_handlers.router)
        dp.include_router(user_handlers.router)

        # Удаляем вебхук и запускаем поллинг
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Starting polling...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Приложение завершено")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")