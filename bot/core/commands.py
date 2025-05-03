"""
Модуль для управления командами бота.
"""

from typing import List
from aiogram import Bot, types
import logging

logger = logging.getLogger(__name__)

# Список команд бота
BOT_COMMANDS = [
    {
        "command": "start",
        "description": "Запустить бота"
    },
    {
        "command": "profile",
        "description": "Показать профиль"
    },
    {
        "command": "help",
        "description": "Показать справку"
    }
]

async def set_bot_commands(bot: Bot) -> None:
    """
    Установка команд бота.
    
    Args:
        bot: Объект бота
    """
    try:
        commands = [
            types.BotCommand(
                command=cmd["command"],
                description=cmd["description"]
            )
            for cmd in BOT_COMMANDS
        ]
        await bot.set_my_commands(commands)
        logger.info("Команды бота успешно установлены")
    except Exception as e:
        logger.error(f"Ошибка при установке команд бота: {str(e)}")
        raise 