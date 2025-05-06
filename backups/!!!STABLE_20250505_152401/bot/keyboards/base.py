"""
Базовый модуль для клавиатур.
Содержит функции для создания различных типов клавиатур.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Optional
from ..database.sql_models import Admin

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
    Создает клавиатуру для администраторов.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура администратора
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Список Админов"))
    keyboard.add(KeyboardButton("✅ Добавить Админ"), KeyboardButton("❌ Удалить Админ"))
    keyboard.add(KeyboardButton("🔍 Посмотреть Уровни"), KeyboardButton("✏️ Редактировать Уровни"))
    keyboard.add(KeyboardButton("🔄 Обновить"))
    return keyboard

def get_levels_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для редактирования уровней.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура редактирования уровней
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("1️⃣ Уровень 1", callback_data="edit_level_1"),
        InlineKeyboardButton("2️⃣ Уровень 2", callback_data="edit_level_2"),
        InlineKeyboardButton("3️⃣ Уровень 3", callback_data="edit_level_3"),
        InlineKeyboardButton("4️⃣ Уровень 4", callback_data="edit_level_4")
    )
    return keyboard

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру подтверждения.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_level_change"),
        InlineKeyboardButton("❌ Отменить", callback_data="cancel_level_change")
    )
    return keyboard

def get_admin_remove_keyboard(admins: List[Admin]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для удаления администраторов.
    
    Args:
        admins: Список администраторов
        
    Returns:
        InlineKeyboardMarkup: Клавиатура удаления администраторов
    """
    keyboard = InlineKeyboardMarkup()
    for admin in admins:
        if not admin.is_main:  # Не показываем главного админа
            keyboard.add(InlineKeyboardButton(
                text=f"❌ {admin.first_name} {admin.last_name} (@{admin.username or 'нет'})",
                callback_data=f"remove_admin_{admin.telegram_id}"
            ))
    return keyboard 