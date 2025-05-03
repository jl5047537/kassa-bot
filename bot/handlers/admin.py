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
    # TODO: Получить список администраторов из БД
    admins = []  # Временное значение
    if not admins:
        await message.answer("Список администраторов пуст.")
        return
    
    text = "👥 *Список администраторов:*\n\n"
    for admin in admins:
        text += f"• {admin['first_name']} {admin['last_name']} (@{admin['username']})\n"
    
    await message.answer(text, parse_mode="Markdown")

async def add_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID нового администратора.
    
    Args:
        message: Объект сообщения
    """
    await message.answer(
        "Введите ID пользователя, которого хотите сделать администратором:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # TODO: Установить состояние ожидания ID

async def remove_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID администратора для удаления.
    
    Args:
        message: Объект сообщения
    """
    await message.answer(
        "Введите ID администратора, которого хотите удалить:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # TODO: Установить состояние ожидания ID

async def edit_levels(message: types.Message) -> None:
    """
    Показывает меню редактирования уровней.
    
    Args:
        message: Объект сообщения
    """
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
    dp.register_message_handler(show_admins_list, lambda msg: msg.text == "👥 Список администраторов")
    dp.register_message_handler(add_admin_prompt, lambda msg: msg.text == "➕ Добавить администратора")
    dp.register_message_handler(remove_admin_prompt, lambda msg: msg.text == "➖ Удалить администратора")
    dp.register_message_handler(edit_levels, lambda msg: msg.text == "📊 Редактировать уровни") 