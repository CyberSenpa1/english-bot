from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import text
from os import getenv
from typing import AsyncGenerator
import logging
import csv
from db.models import words, metadata
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Конфигурация подключения к PostgreSQL
POSTGRES_CONFIG = {
    "user": getenv("POSTGRES_USER", "english_bot"),
    "password": getenv("POSTGRES_PASSWORD", "default_password"),
    "db": getenv("POSTGRES_DB", "vocabmaster"),
    "host": getenv("POSTGRES_HOST", "db"),
    "port": getenv("POSTGRES_PORT", "5432")
}

DATABASE_URL = getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
    f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['db']}"
)

# Настройка движка SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=True,  # Включаем логирование SQL-запросов для отладки
    future=True
)

# Фабрика сессий
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)

async def init_db():
    from .models import metadata
    logger = logging.getLogger(__name__)
    logger.warning("!!! ВЫЗОВ init_db() !!!")
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        logger.info("Creating all database tables if not exist...")
        await conn.run_sync(metadata.create_all)
        logger.info("Tables checked/created successfully")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий с обработкой ошибок"""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def close_redis():
    """Корректно закрывает соединение с Redis"""
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            await redis_client.wait_closed()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        finally:
            redis_client = None

async def some_async_function(user_id):
    # Пример асинхронной функции, где может использоваться проверка существующего пользователя
    async with get_db() as session:
        result = await session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            logger.info("Пользователь не найден, создаем нового")
            # Логика создания нового пользователя
        else:
            logger.info("Пользователь найден, обновляем данные")
            # Логика обновления данных существующего пользователя

async def download_words():
    logger.info("=== ЗАПУСК download_words ===")
    async with engine.begin() as conn:
        with open("db/words.csv", "r") as file:
            csv_reader = csv.DictReader(file, skipinitialspace=True)
            rows = []
            for row in csv_reader:
                row['difficulty_level'] = int(row['difficulty_level'].strip())
                row['english'] = row['english'].strip()
                row['russian'] = row['russian'].strip()
                row['part_of_speech'] = row['part_of_speech'].strip()
                rows.append(row)
            if rows:
                stmt = pg_insert(words).values(rows).on_conflict_do_nothing(index_elements=['english'])
                await conn.execute(stmt)
            logger.info(f"Rows to insert: {len(rows)}")
        logger.info("Words downloaded and inserted into the database")

async def get_redis():
    redis_host = getenv("REDIS_HOST", "redis")
    redis_port = int(getenv("REDIS_PORT", 6379))
    redis_db = int(getenv("REDIS_DB", 0))
    return aioredis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)