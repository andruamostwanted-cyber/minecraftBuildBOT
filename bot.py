import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TOKEN
from commands import set_bot_commands
from handlers import router
from admin_handlers import admin_router
from contact_handlers import contact_router
from db.session import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Инициализация бота и диспетчера
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.include_router(router)
dp.include_router(admin_router)
dp.include_router(contact_router) 

async def on_startup():
    """Действия при запуске бота"""
    logging.info("Starting Minecraft Build Bot...")
    
    # Инициализируем базу данных
    await init_db()
    logging.info("Database initialized")
    
    # Устанавливаем команды в меню
    await set_bot_commands(bot)
    
    # Если есть URL для вебхука (продакшен), настраиваем его
    if 'RAILWAY_STATIC_URL' in os.environ:
        webhook_url = f"{os.environ['RAILWAY_STATIC_URL']}/webhook"
        await bot.set_webhook(webhook_url)
        logging.info(f"Webhook set to: {webhook_url}")
    else:
        # Локальная разработка - polling
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook deleted, starting polling...")

async def on_shutdown():
    """Действия при остановке бота"""
    logging.info("Shutting down...")
    await bot.session.close()

async def main():
    """Основная функция запуска бота"""
    await on_startup()
    
    # Проверяем окружение - вебхук или polling
    if 'RAILWAY_STATIC_URL' in os.environ:
        # Продакшен режим - вебхук
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        port = int(os.environ.get("PORT", 8000))
        return app
    else:
        # Локальная разработка - polling
        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown()

if __name__ == "__main__":
    if 'RAILWAY_STATIC_URL' in os.environ:
        # Запуск для Railway
        app = asyncio.run(main())
        web.run_app(app, port=int(os.environ.get("PORT", 8000)), host='0.0.0.0')
    else:
        # Локальный запуск
        asyncio.run(main())