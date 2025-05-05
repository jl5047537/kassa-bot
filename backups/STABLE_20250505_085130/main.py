"""
Основной модуль бота.
"""

import logging
import asyncio
import sys
from aiogram import Dispatcher, Bot, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .core.config import settings
from .core.bot_init import init_bot, TokenValidationError
from .core.commands import set_bot_commands
from .core.error_handler import error_handler
from .core.backup_manager import BackupManager
from .core.backup_scheduler import BackupScheduler
from .core.logger import logger, setup_logging
from .core.database import db
from .handlers.admin import register_admin_handlers
from .handlers.user import register_user_handlers

# Инициализация логгера
setup_logging()

try:
    # Инициализация бота и диспетчера
    bot, dp = init_bot(settings.TELEGRAM_BOT_TOKEN)
except TokenValidationError as e:
    logger.critical(f"Критическая ошибка: {str(e)}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Критическая ошибка при инициализации бота: {str(e)}")
    sys.exit(1)

# Инициализация менеджера бэкапов и планировщика
backup_manager = BackupManager(bot=bot)
backup_scheduler = BackupScheduler(backup_manager)

@error_handler
async def on_startup(dp: Dispatcher) -> None:
    """
    Действия при запуске бота.
    
    Args:
        dp: Диспетчер бота
    """
    try:
        # Запускаем планировщик бэкапов
        await backup_scheduler.start()
        
        # Создаем начальный бэкап
        await backup_manager.create_backup()
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        
        logger.info("Starting bot...", extra={
            "bot_id": bot_info.id,
            "bot_username": bot_info.username
        })
        
        # Инициализируем главного администратора
        if not db.is_admin(settings.MAIN_ADMIN_ID):
            db.add_admin(
                user_id=settings.MAIN_ADMIN_ID,
                username="main_admin",
                first_name="Main",
                last_name="Admin",
                is_main=True
            )
            logger.info("Main admin initialized")
        
        # Регистрация обработчиков
        register_admin_handlers(dp)
        register_user_handlers(dp)
        
        # Установка команд бота
        await set_bot_commands(dp)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        raise

@error_handler
async def on_shutdown(dp: Dispatcher) -> None:
    """
    Действия при выключении бота.
    
    Args:
        dp: Диспетчер бота
    """
    try:
        # Останавливаем планировщик бэкапов
        await backup_scheduler.stop()
        
        # Создаем финальный бэкап
        await backup_manager.create_backup()
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        
        logger.info("Shutting down bot...", extra={
            "bot_id": bot_info.id,
            "bot_username": bot_info.username
        })
        
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"Ошибка при выключении бота: {str(e)}")
        raise

@error_handler
async def main() -> None:
    """
    Основная функция запуска бота.
    """
    try:
        # Запуск бота
        await on_startup(dp)
        await dp.start_polling()
    finally:
        await on_shutdown(dp)

if __name__ == "__main__":
    # Запуск бота
    asyncio.run(main()) 