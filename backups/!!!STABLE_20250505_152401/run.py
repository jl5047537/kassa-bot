"""
Скрипт запуска бота.
"""

import os
from pathlib import Path
from bot.main import dp, on_startup, on_shutdown
from bot.core.config import settings
from bot.core.logger import setup_logging
import logging

# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
config_path = Path('config.env')
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
else:
    logger.warning("Файл config.env не найден")

if __name__ == '__main__':
    logger.info("Starting bot...", extra={
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION
    })
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown) 