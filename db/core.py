from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from .models import metadata
from os import getenv
from redis.asyncio import Redis
from typing import AsyncGenerator
import logging
import pandas as pd

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

# Redis клиент с повторными попытками подключения
async def create_redis_client():
    """Создает клиент Redis с обработкой ошибок"""
    return Redis(
        host=getenv("REDIS_HOST", "redis"),
        port=int(getenv("REDIS_PORT", 6379)),
        db=int(getenv("REDIS_DB", 0)),
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )

redis_client = None

async def get_redis() -> Redis:
    """Получает клиент Redis с проверкой подключения"""
    global redis_client
    if not redis_client:
        redis_client = await create_redis_client()
    
    try:
        await redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        # Попытка переподключения
        redis_client = await create_redis_client()
        return redis_client

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