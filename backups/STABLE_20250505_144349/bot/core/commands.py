"""
Модуль для управления командами бота.
"""

from typing import List
from aiogram import Dispatcher, types
import logging

logger = logging.getLogger(__name__)

# Список команд бота
BOT_COMMANDS = [
    {
        "command": "start",
        "description": "Запустить бота"
    }
]

async def set_bot_commands(dp: Dispatcher) -> None:
    """
    Установка команд бота.
    
    Args:
        dp: Диспетчер бота
    """
    try:
        commands = [
            types.BotCommand(
                command=cmd["command"],
                description=cmd["description"]
            )
            for cmd in BOT_COMMANDS
        ]
        await dp.bot.set_my_commands(commands)
        logger.info(f"Команды бота установлены: {commands}")
    except Exception as e:
        logger.error(f"Ошибка при установке команд бота: {str(e)}")
        raise 