from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_bot_commands(bot: Bot):
    """Установка команд бота для меню"""
    commands = [
        BotCommand(command="start", description="🎮 Начать работу с ботом"),
        BotCommand(command="random_build", description="🎲 Случайная сборка"),
        BotCommand(command="build_filters", description="🔍 Подбор по фильтрам"),
    ]
    
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
