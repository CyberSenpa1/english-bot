import os
import asyncio
import logging
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from handlers import user_handlers, admin_handlers, trainer, user_stats, user_settings
from handlers.admin_handlers import notify_admins_on_start
from db.core import init_db, download_words

from middlewares.redis import RedisMiddleware
from db.core import get_redis

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
    try:
        await download_words()
        logger.info("Слова успешно загружены в базу данных")
    except Exception as e:
        logger.error(f"Ошибка при загрузке слов: {e}", exc_info=True)
        raise
        

async def on_shutdown(dispatcher: Dispatcher):
    """Действия при остановке бота"""
    try:
        await dispatcher.emit_shutdown()
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
        await download_words()
        logger.info("Слова успешно загружены в базу данных")

        # Инициализация бота
        bot = Bot(token=getenv("BOT_TOKEN"))

        await notify_admins_on_start(bot)

        # Инициализация хранилища FSM
        redis = await get_redis()
        storage = RedisStorage(redis)


        # Создание диспетчера
        dp = Dispatcher(storage=storage)

        # Подключаем middleware для redis
        dp.message.middleware(RedisMiddleware(redis))
        dp.callback_query.middleware(RedisMiddleware(redis))

        
        dp.include_routers(
            admin_handlers.router,
            user_handlers.router,
            trainer.router,
            user_stats.router,
            user_settings.router
            )
        
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