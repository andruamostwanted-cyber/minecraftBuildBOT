import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.models import Base


# Определяем URL базы данных в зависимости от окружения
def get_database_url():
    if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'].startswith('postgresql'):
        # Для PostgreSQL на Railway
        return os.environ['DATABASE_URL'].replace('postgresql', 'postgresql+asyncpg')
    else:
        # Локальная SQLite
        return "sqlite+aiosqlite:///./minecraft_bot.db"

DATABASE_URL = get_database_url()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Отключаем логирование в продакшене
    future=True
)

# Для PostgreSQL нужно увеличить пул соединений
if DATABASE_URL.startswith('postgresql'):
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=20,
        max_overflow=30
    )

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)