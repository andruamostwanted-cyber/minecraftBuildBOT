import os
from  config import TOKEN, ADMIN_IDS

class ProductionConfig:
    BOT_TOKEN = TOKEN
    ADMIN_IDS = ADMIN_IDS
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./minecraft_bot.db')
    
    # Для Railway используем PostgreSQL если доступно
    if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'].startswith('postgresql'):
        DATABASE_URL = os.environ['DATABASE_URL'].replace('postgresql', 'postgresql+asyncpg')

production_config = ProductionConfig()