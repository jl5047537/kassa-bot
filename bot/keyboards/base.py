"""
Базовый модуль для клавиатур.
Содержит функции для создания различных типов клавиатур.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Optional

def get_main_keyboard(user_id: Optional[str] = None) -> ReplyKeyboardMarkup:
    """
    Создает основную клавиатуру в зависимости от уровня пользователя.
    
    Args:
        user_id: ID пользователя в Telegram
        
    Returns:
        ReplyKeyboardMarkup: Основная клавиатура
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    if user_id:
        # TODO: Получить уровень пользователя из БД
        user_level = 0  # Временное значение
        if user_level > 0:
            # Для активных пользователей
            keyboard.add(KeyboardButton("👥 Пригласить Друзей"))
            keyboard.add(KeyboardButton("📊 Профиль"))
            keyboard.add(KeyboardButton("❓ Помощь"))
        else:
            # Для неактивных пользователей
            keyboard.add(KeyboardButton("🔑 Стартовый Ключ"))
            keyboard.add(KeyboardButton("📊 Профиль"), KeyboardButton("❓ Помощь"))
    else:
        # Базовые кнопки
        keyboard.add(KeyboardButton("🔑 Стартовый Ключ"))
        keyboard.add(KeyboardButton("📊 Профиль"), KeyboardButton("❓ Помощь"))
    
    return keyboard

def get_registration_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для регистрации.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура регистрации
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔑 Зарегистрироваться", request_contact=True))
    return keyboard

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для администратора.
    
    Returns:
        ReplyKeyboardMarkup: Административная клавиатура
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Список Администраторов"))
    keyboard.add(KeyboardButton("➕ Добавить Админа"))
    keyboard.add(KeyboardButton("➖ Удалить Админа"))
    keyboard.add(KeyboardButton("✏️ Редактировать Уровни"))
    return keyboard 