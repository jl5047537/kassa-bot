"""
Модуль обработчиков администраторов.
Содержит обработчики команд и сообщений для администраторов.
"""

import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Optional

from ..core.config import settings
from ..keyboards.base import get_admin_keyboard
from ..utils.validators import validate_field

logger = logging.getLogger(__name__)

async def cmd_admin(message: types.Message) -> None:
    """
    Обработчик команды /admin.
    
    Args:
        message: Объект сообщения
    """
    user_id = message.from_user.id
    if user_id != settings.MAIN_ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    keyboard = get_admin_keyboard()
    await message.answer(
        "🌟 *Добро пожаловать в центр управления успехом!* 🌟\n\n"
        "*Наш Божественный Админ*, ваша энергия и лидерство — настоящий двигатель этого проекта! 🚀\n"
        "Вы не просто управляете процессами — вы вдохновляете!\n\n"
        "*Сегодня снова ваш день творить великие перемены!* 🔥",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def show_admins_list(message: types.Message) -> None:
    """
    Показывает список администраторов.
    
    Args:
        message: Объект сообщения
    """
    user_id = str(message.from_user.id)
    if int(user_id) != settings.MAIN_ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    logger.info(f"Admin {user_id} requested admins list")
    
    # TODO: Получить список администраторов из БД
    # Временно добавляем главного администратора
    main_admin = {
        'id': settings.MAIN_ADMIN_ID,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name or '',
        'username': message.from_user.username or 'нет',
        'level': '👼 Бог (Гл. админ) 🙏'
    }
    
    text = "👥 *Список администраторов:*\n\n"
    text += f"• {main_admin['first_name']} {main_admin['last_name']} (@{main_admin['username']})\n"
    text += f"  └ ID: {main_admin['id']}\n"
    text += f"  └ Уровень: {main_admin['level']}\n"
    
    await message.answer(text, parse_mode="Markdown")

async def add_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID нового администратора.
    
    Args:
        message: Объект сообщения
    """
    user_id = str(message.from_user.id)
    if int(user_id) != settings.MAIN_ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    logger.info(f"Admin {user_id} requested to add new admin")
    
    await message.answer(
        "Введите ID пользователя, которого хотите сделать администратором:"
    )
    # TODO: Установить состояние ожидания ID

async def remove_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID администратора для удаления.
    
    Args:
        message: Объект сообщения
    """
    user_id = str(message.from_user.id)
    if int(user_id) != settings.MAIN_ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    logger.info(f"Admin {user_id} requested to remove admin")
    
    await message.answer(
        "Введите ID администратора, которого хотите удалить:"
    )
    # TODO: Установить состояние ожидания ID

async def edit_levels(message: types.Message) -> None:
    """
    Показывает меню редактирования уровней.
    
    Args:
        message: Объект сообщения
    """
    user_id = str(message.from_user.id)
    if int(user_id) != settings.MAIN_ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    logger.info(f"Admin {user_id} requested to edit levels")
    
    # TODO: Реализовать меню редактирования уровней
    await message.answer("Функция редактирования уровней в разработке.")

def register_admin_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует обработчики для администраторов.
    
    Args:
        dp: Диспетчер бота
    """
    # Регистрация обработчиков команд
    dp.register_message_handler(cmd_admin, commands=["admin"])
    dp.register_message_handler(show_admins_list, lambda msg: msg.text == "👥 Список Администраторов")
    dp.register_message_handler(add_admin_prompt, lambda msg: msg.text == "➕ Добавить Админа")
    dp.register_message_handler(remove_admin_prompt, lambda msg: msg.text == "➖ Удалить Админа")
    dp.register_message_handler(edit_levels, lambda msg: msg.text == "✏️ Редактировать Уровни") 