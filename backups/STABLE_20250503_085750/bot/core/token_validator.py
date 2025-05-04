"""
Модуль для валидации токена бота.
"""

import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)

class TokenValidationError(Exception):
    """Исключение для ошибок валидации токена."""
    pass

def validate_token(token: str) -> Tuple[bool, str]:
    """
    Проверяет валидность токена бота.
    
    Args:
        token: Токен для проверки
        
    Returns:
        Tuple[bool, str]: (результат проверки, сообщение об ошибке)
    """
    # Проверка на пустой токен
    if not token:
        return False, "Токен бота пустой"
    
    # Проверка на пробелы
    if ' ' in token:
        return False, "Токен не должен содержать пробелы"
    
    # Проверка формата (пример: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
    parts = token.split(':')
    if len(parts) != 2:
        return False, "Неверный формат токена. Должен быть в формате 'ID:TOKEN'"
    
    # Проверка что первая часть - это число
    if not parts[0].isdigit():
        return False, "ID бота должен быть числом"
    
    # Проверка длины второй части
    if len(parts[1]) < 10:
        return False, "Слишком короткий токен"
    
    # Проверка символов в токене
    if not re.match(r'^[A-Za-z0-9_-]+$', parts[1]):
        return False, "Токен содержит недопустимые символы"
    
    return True, "Токен валидный"

def get_token_info(token: str) -> dict:
    """
    Получает информацию о токене.
    
    Args:
        token: Токен для анализа
        
    Returns:
        dict: Информация о токене
    """
    parts = token.split(':')
    return {
        'bot_id': parts[0],
        'token_length': len(parts[1]),
        'is_valid': validate_token(token)[0]
    } 