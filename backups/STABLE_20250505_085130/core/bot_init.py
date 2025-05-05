"""
Модуль для инициализации бота и диспетчера.
"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from .token_validator import validate_token, TokenValidationError

logger = logging.getLogger(__name__)

def init_bot(token: str) -> tuple[Bot, Dispatcher]:
    """
    Инициализация бота и диспетчера.
    
    Args:
        token: Токен бота
        
    Returns:
        tuple[Bot, Dispatcher]: Кортеж с ботом и диспетчером
        
    Raises:
        TokenValidationError: Если токен невалидный
    """
    try:
        # Валидация токена
        is_valid, error_message = validate_token(token)
        if not is_valid:
            logger.error(f"Ошибка валидации токена: {error_message}")
            raise TokenValidationError(error_message)
            
        logger.info("Токен успешно валидирован")
        
        # Создание бота и диспетчера
        bot = Bot(token=token)
        storage = MemoryStorage()
        dp = Dispatcher(bot, storage=storage)
        
        logger.info("Бот и диспетчер успешно инициализированы")
        return bot, dp
        
    except TokenValidationError as e:
        logger.error(f"Ошибка валидации токена: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при инициализации бота: {str(e)}")
        raise 