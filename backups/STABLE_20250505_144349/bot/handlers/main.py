"""
Модуль основных обработчиков.
Содержит обработчики команд и сообщений для всех пользователей.
"""

import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from ..core.config import settings
from ..keyboards.base import get_main_keyboard, get_registration_keyboard
from ..utils.validators import validate_field
from ..states.main import MainStates
from ..core.database import db
from ..constants.messages import (
    WELCOME, WELCOME_ADMIN, WELCOME_USER, ERROR_GENERAL,
    ERROR_NOT_FOUND, ERROR_RIGHTS, ERROR_INVALID_FORMAT,
    PHONE_VALIDATION_ERROR, PHONE_DUPLICATE_ERROR,
    REGISTRATION_SUCCESS, REGISTRATION_ERROR
)

logger = logging.getLogger(__name__)

async def start(message: types.Message) -> None:
    """
    Обрабатывает команду /start.
    
    Args:
        message: Объект сообщения
    """
    try:
        # Проверяем, является ли пользователь администратором
        is_admin = db.is_admin(message.from_user.id)
        
        # Отправляем приветственное сообщение
        if is_admin:
            await message.answer(
                WELCOME_ADMIN,
                reply_markup=get_main_keyboard(is_admin=True)
            )
        else:
            await message.answer(
                WELCOME_USER,
                reply_markup=get_main_keyboard(is_admin=False)
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /start: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=ReplyKeyboardRemove()
        )

async def help_command(message: types.Message) -> None:
    """
    Обрабатывает команду /help.
    
    Args:
        message: Объект сообщения
    """
    try:
        # Проверяем, является ли пользователь администратором
        is_admin = db.is_admin(message.from_user.id)
        
        # Формируем текст помощи
        help_text = (
            "🤖 *Помощь*\n\n"
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/register - Зарегистрироваться\n"
        )
        
        if is_admin:
            help_text += (
                "\nКоманды администратора:\n"
                "/admin - Открыть админ-панель\n"
                "/users - Показать список пользователей\n"
                "/add_user - Добавить пользователя\n"
                "/remove_user - Удалить пользователя\n"
                "/edit_user - Редактировать пользователя\n"
            )
            
        await message.answer(help_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /help: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=ReplyKeyboardRemove()
        )

async def register_prompt(message: types.Message) -> None:
    """
    Запрашивает данные для регистрации.
    
    Args:
        message: Объект сообщения
    """
    try:
        await message.answer(
            "📱 Введите номер телефона для регистрации:",
            reply_markup=ReplyKeyboardRemove()
        )
        await MainStates.waiting_for_phone.set()
    except Exception as e:
        logger.error(f"Ошибка при запросе данных для регистрации: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=get_main_keyboard(is_admin=False)
        )

async def process_phone(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод номера телефона.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    try:
        # Проверяем формат номера телефона
        phone = message.text.strip()
        
        # Проверяем, что номер начинается с 7 или 8
        if not phone.startswith(('7', '8')):
            await message.answer(PHONE_VALIDATION_ERROR)
            return
            
        # Проверяем, что номер состоит только из цифр и имеет правильную длину
        if not phone.isdigit() or len(phone) != 11:
            await message.answer(PHONE_VALIDATION_ERROR)
            return
            
        # Проверяем уникальность номера телефона
        existing_user = db.get_user_by_phone(phone)
        if existing_user:
            await message.answer(
                PHONE_DUPLICATE_ERROR.format(level=existing_user.level)
            )
            return
            
        # Сохраняем номер телефона в состоянии
        await state.update_data(phone=phone)
        
        # Запрашиваем имя
        await message.answer(
            "👤 Введите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
        )
        await MainStates.waiting_for_name.set()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ввода номера телефона: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=get_main_keyboard(is_admin=False)
        )
        await state.finish()

async def process_name(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод имени.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    try:
        # Проверяем формат имени
        name = message.text.strip()
        if not name or len(name) < 2:
            await message.answer(
                "❌ Имя должно содержать не менее 2 символов.\n"
                "Пожалуйста, введите ваше имя:"
            )
            return
            
        # Сохраняем имя в состоянии
        await state.update_data(name=name)
        
        # Запрашиваем фамилию
        await message.answer(
            "👥 Введите вашу фамилию:",
            reply_markup=ReplyKeyboardRemove()
        )
        await MainStates.waiting_for_surname.set()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ввода имени: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=get_main_keyboard(is_admin=False)
        )
        await state.finish()

async def process_surname(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод фамилии.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    try:
        # Проверяем формат фамилии
        surname = message.text.strip()
        if not surname or len(surname) < 2:
            await message.answer(
                "❌ Фамилия должна содержать не менее 2 символов.\n"
                "Пожалуйста, введите вашу фамилию:"
            )
            return
            
        # Получаем сохраненные данные
        data = await state.get_data()
        phone = data.get('phone')
        name = data.get('name')
        
        if not phone or not name:
            await message.answer(ERROR_NOT_FOUND)
            return
            
        # Добавляем пользователя в БД
        if db.add_user(phone, name, surname):
            await message.answer(
                REGISTRATION_SUCCESS.format(
                    name=name,
                    surname=surname,
                    phone=phone
                ),
                reply_markup=get_main_keyboard(is_admin=False)
            )
        else:
            await message.answer(
                REGISTRATION_ERROR,
                reply_markup=get_main_keyboard(is_admin=False)
            )
            
        # Завершаем текущее состояние
        await state.finish()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ввода фамилии: {str(e)}")
        await message.answer(
            ERROR_GENERAL,
            reply_markup=get_main_keyboard(is_admin=False)
        )
        await state.finish() 