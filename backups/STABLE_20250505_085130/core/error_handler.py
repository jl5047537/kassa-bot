"""
Модуль для обработки ошибок бота.
"""

from typing import Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def error_handler(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок.
    
    Args:
        func: Функция для обработки
        
    Returns:
        Callable: Обернутая функция
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Ошибка в {func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            # Здесь можно добавить дополнительную логику обработки ошибок
            raise
    return wrapper 