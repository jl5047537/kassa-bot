"""
Модуль с функциями валидации данных.
"""

import re
from typing import Optional, Tuple

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Валидация номера телефона.
    
    Args:
        phone: Номер телефона для проверки
        
    Returns:
        Tuple[bool, str]: (Результат валидации, Сообщение об ошибке)
    """
    # Удаляем все нецифровые символы
    cleaned_phone = re.sub(r'\D', '', phone)
    
    # Проверяем длину номера
    if len(cleaned_phone) != 11:
        return False, "Номер телефона должен содержать 11 цифр"
    
    # Проверяем, что номер начинается с 7 или 8
    if not cleaned_phone.startswith(('7', '8')):
        return False, "Номер телефона должен начинаться с 7 или 8"
    
    return True, ""

def validate_name(name: str) -> Tuple[bool, str]:
    """
    Валидация имени или фамилии.
    
    Args:
        name: Имя или фамилия для проверки
        
    Returns:
        Tuple[bool, str]: (Результат проверки, Сообщение об ошибке)
    """
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z0-9\s-]+$', name):
        return False, "❌ Имя/Фамилия могут содержать только буквы, цифры, пробелы и дефисы"
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Валидация имени пользователя.
    
    Args:
        username: Имя пользователя для проверки
        
    Returns:
        Tuple[bool, str]: (Результат проверки, Сообщение об ошибке)
    """
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "❌ Username может содержать только латинские буквы, цифры и подчеркивания"
    return True, ""

def validate_field(field: str, field_type: str) -> Tuple[bool, str]:
    """
    Валидация поля в зависимости от его типа.
    
    Args:
        field: Значение поля
        field_type: Тип поля (phone, name, etc.)
        
    Returns:
        Tuple[bool, str]: (Результат валидации, Сообщение об ошибке)
    """
    if not field:
        return False, "Поле не может быть пустым"
    
    if field_type == "phone":
        return validate_phone(field)
    elif field_type in ["first_name", "last_name"]:
        return validate_name(field)
    elif field_type == "username":
        return validate_username(field)
    
    # TODO: Добавить валидацию других типов полей
    
    return True, "" 