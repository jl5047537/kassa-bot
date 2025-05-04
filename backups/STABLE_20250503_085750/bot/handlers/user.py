"""
Модуль обработчиков пользователей.
Содержит обработчики команд и сообщений для пользователей.
"""

import logging
import hashlib
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Optional

from ..core.config import settings
from ..keyboards.base import get_main_keyboard, get_registration_keyboard, get_admin_keyboard
from ..utils.validators import validate_field

logger = logging.getLogger(__name__)

def get_referral_id(phone_number: Optional[str]) -> str:
    """
    Генерирует referral ID на основе номера телефона.
    
    Args:
        phone_number: Номер телефона
        
    Returns:
        str: Referral ID
    """
    if not phone_number:
        return "нет данных"
    phone_bytes = phone_number.encode('utf-8')
    hash_object = hashlib.md5(phone_bytes)
    hash_hex = hash_object.hexdigest()
    return hash_hex[:8]

async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    user_id = str(message.from_user.id)
    username = message.from_user.username
    
    logger.info(f"User started bot: id={user_id}, username={username}")
    
    # Сохраняем реферальный ID если он есть
    args = message.get_args()
    if args:
        await state.update_data(referrer_id=args)
        logger.info(f"Saved referrer_id: {args} for user {user_id}")
    
    # Для всех пользователей показываем приветствие и кнопку регистрации
    await message.answer(
        "🚀 *Добро пожаловать!*\n"
        "Твой путь к финансовой свободе начинается здесь!\n"
        "Пройди короткую регистрацию в нашей *Кассе Взаимопомощи* и начни строить своё уверенное будущее уже сегодня. 🔥\n"
        "Готов? Жми кнопку ниже! 👇",
        parse_mode="Markdown",
        reply_markup=get_registration_keyboard()
    )
    
    # Устанавливаем состояние ожидания контакта
    await state.set_state("waiting_for_phone")

async def handle_contact(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик получения контакта пользователя.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    user_id = str(message.from_user.id)
    contact = message.contact
    
    logger.info(f"Received contact from user {user_id}: {contact.phone_number}")
    
    # Проверяем, является ли пользователь главным администратором
    if int(user_id) == settings.MAIN_ADMIN_ID:
        # Для главного администратора показываем панель администратора
        keyboard = get_admin_keyboard()
        await message.answer(
            "🌟 *Добро пожаловать в центр управления успехом!* 🌟\n\n"
            "*Наш Божественный Админ*, ваша энергия и лидерство — настоящий двигатель этого проекта! 🚀\n"
            "Вы не просто управляете процессами — вы вдохновляете!\n\n"
            "*Сегодня снова ваш день творить великие перемены!* 🔥",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        # Для обычных пользователей показываем основное меню
        keyboard = get_main_keyboard(user_id)
        await message.answer(
            "✅ Регистрация успешно завершена!\n\n"
            "Теперь вы можете:\n"
            "• Приглашать друзей\n"
            "• Просматривать свой профиль\n"
            "• Получать помощь\n\n"
            "Выберите действие:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    # Сбрасываем состояние
    await state.finish()

async def show_profile(message: types.Message) -> None:
    """
    Показывает профиль пользователя.
    
    Args:
        message: Объект сообщения
    """
    # TODO: Получить данные пользователя из БД
    user = None  # Временное значение
    if not user:
        await message.answer(
            "Для начала работы зарегистрируйтесь:",
            reply_markup=get_registration_keyboard()
        )
        return
    
    ref_id = get_referral_id(user.get('phone_number'))
    referrals_count = 0  # TODO: Получить количество рефералов
    
    # Формируем текст с уровнями и прогрессом
    levels_text = ""
    
    # Используем новую структуру уровней из настроек
    level_requirements = {
        1: settings.LEVEL_1_REQUIREMENT,
        2: settings.LEVEL_2_REQUIREMENT,
        3: settings.LEVEL_3_REQUIREMENT
    }
    
    current_level = user.get('level', 0)
    for level, required_referrals in level_requirements.items():
        is_current = level == current_level
        is_completed = level < current_level
        is_locked = level > current_level
        
        level_emoji = "✅" if is_completed else "🔒" if is_locked else "🏆" if is_current else "🏃"
        level_status = " (Текущий)" if is_current else " (Заблокирован)" if is_locked else " (Завершен)" if is_completed else ""
        
        progress = f"{referrals_count}/{required_referrals}" if not is_completed else "✅"
        
        levels_text += f"{level_emoji} {level} уровень {level_status} - {progress}\n"
    
    profile_text = (
        f"👤 *Ваш профиль*\n\n"
        f"📱 Телефон: {user.get('phone_number', 'не указан')}\n"
        f"🆔 Ваш referral ID: *{ref_id}*\n"
        f"👥 Приглашено друзей: *{referrals_count}*\n\n"
        f"*Уровни:*\n{levels_text}"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")

async def show_rules(message: types.Message) -> None:
    """
    Показывает правила системы.
    
    Args:
        message: Объект сообщения
    """
    rules_text = (
        "📜 *Правила Кассы Взаимопомощи*\n\n"
        "1. *Регистрация*\n"
        "   • Регистрация обязательна для всех участников\n"
        "   • Используйте только реальные данные\n"
        "   • Один человек - один аккаунт\n\n"
        "2. *Реферальная система*\n"
        "   • Приглашайте друзей через свой реферальный ID\n"
        "   • За каждого приглашенного получайте бонусы\n"
        "   • Не используйте накрутку рефералов\n\n"
        "3. *Уровни*\n"
        "   • Уровень повышается при достижении определенного количества рефералов\n"
        "   • Чем выше уровень - тем больше возможностей\n"
        "   • Уровни нельзя передавать или продавать\n\n"
        "4. *Общение*\n"
        "   • Уважайте других участников\n"
        "   • Не спамьте и не флудите\n"
        "   • Соблюдайте правила чата\n\n"
        "5. *Безопасность*\n"
        "   • Не передавайте свои данные третьим лицам\n"
        "   • Сообщайте о подозрительной активности\n"
        "   • Используйте только официальные каналы связи"
    )
    await message.answer(rules_text, parse_mode="Markdown")

async def show_help(message: types.Message) -> None:
    """
    Показывает справочную информацию.
    
    Args:
        message: Объект сообщения
    """
    help_text = (
        "🌟 *Добро пожаловать в Кассу Взаимопомощи!*\n\n"
        "*Основные команды:*\n"
        "• /start - Начать работу с ботом\n"
        "• /profile - Показать ваш профиль\n"
        "• /help - Показать эту справку\n\n"
        "*Как это работает:*\n"
        "1. Зарегистрируйтесь, указав свой номер телефона\n"
        "2. Получите свой уникальный реферальный ID\n"
        "3. Приглашайте друзей и повышайте свой уровень\n"
        "4. Чем выше уровень - тем больше возможностей!\n\n"
        "*Уровни и требования:*\n"
        f"• Уровень 1: {settings.LEVEL_1_REQUIREMENT} рефералов\n"
        f"• Уровень 2: {settings.LEVEL_2_REQUIREMENT} рефералов\n"
        f"• Уровень 3: {settings.LEVEL_3_REQUIREMENT} рефералов\n\n"
        "По всем вопросам обращайтесь к администратору."
    )
    await message.answer(help_text, parse_mode="Markdown")

def register_user_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует обработчики для пользователей.
    
    Args:
        dp: Диспетчер бота
    """
    # Регистрация обработчиков команд
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    dp.register_message_handler(handle_contact, content_types=["contact"], state="waiting_for_phone")
    dp.register_message_handler(show_profile, commands=["profile"])
    dp.register_message_handler(show_profile, lambda msg: msg.text == "👤 Профиль")
    dp.register_message_handler(show_help, commands=["help"])
    dp.register_message_handler(show_help, lambda msg: msg.text == "❓ Помощь") 