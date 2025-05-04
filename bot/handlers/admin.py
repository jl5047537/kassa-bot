"""
Модуль обработчиков администраторов.
Содержит обработчики команд и сообщений для администраторов.
"""

import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from ..core.config import settings
from ..keyboards.base import get_admin_keyboard, get_levels_keyboard, get_confirm_keyboard, get_admin_remove_keyboard
from ..utils.validators import validate_field
from ..states.admin import AdminStates
from ..core.database import db

logger = logging.getLogger(__name__)

async def show_admins_list(message: types.Message) -> None:
    """
    Показывает список администраторов.
    
    Args:
        message: Объект сообщения
    """
    try:
        # Логируем нажатие кнопки
        logger.info(f"Пользователь {message.from_user.id} нажал кнопку 'Список Админов'")
        
        # Проверяем права
        user_id = message.from_user.id
        if not db.is_main_admin(user_id):
            logger.warning(f"Пользователь {user_id} пытался просмотреть список админов без прав")
            await message.answer("У вас нет прав для просмотра списка администраторов.")
            return
        
        # Получаем список админов
        admins = db.get_admins()
        logger.info(f"Получено {len(admins)} администраторов из БД")
        
        if not admins:
            logger.info("Список администраторов пуст")
            await message.answer("Список администраторов пуст.")
            return
        
        # Формируем текст
        text = "👥 <b>Список администраторов:</b>\n\n"
        for admin in admins:
            role = "Главный администратор" if admin.is_main else "Администратор"
            text += f"👤 <b>{admin.first_name} {admin.last_name}</b>\n"
            text += f"🆔 ID: <code>{admin.telegram_id}</code>\n"
            text += f"👑 Роль: {role}\n"
            if admin.username:
                text += f"📱 @{admin.username}\n"
            text += "\n"
        
        # Отправляем сообщение
        sent_message = await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
        
        if sent_message:
            logger.info(f"Список администраторов успешно отправлен пользователю {user_id}")
        else:
            logger.error(f"Не удалось отправить список администраторов пользователю {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка при показе списка администраторов: {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_admin_keyboard()
        )

async def add_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID нового администратора.
    
    Args:
        message: Объект сообщения
    """
    user_id = message.from_user.id
    if not db.is_main_admin(user_id):
        await message.answer("У вас нет прав для добавления администраторов.")
        return
    
    await message.answer(
        "Введите ID пользователя, которого хотите сделать администратором:"
    )
    await AdminStates.waiting_for_admin_id.set()

async def process_admin_id(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод ID нового администратора.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    try:
        new_admin_id = int(message.text)
        # Проверяем, не является ли пользователь уже администратором
        if db.is_admin(new_admin_id):
            await message.answer("Этот пользователь уже является администратором.")
            return
        
        # Добавляем нового администратора
        admin = db.add_admin(
            user_id=new_admin_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name or ""
        )
        
        if admin:
            # Завершаем текущее состояние
            await state.finish()
            
            # Устанавливаем состояние админ-панели
            await AdminStates.admin_panel.set()
            
            # Отправляем сообщение об успехе и админ-панель
            await message.answer(
                "✅ Новый администратор успешно добавлен!\n\n"
                "👋 Добро пожаловать в админ-панель!\n\n"
                "Выберите действие:",
                reply_markup=get_admin_keyboard()
            )
        else:
            await message.answer("❌ Не удалось добавить администратора.")
            await state.finish()
            
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя.")
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        await message.answer("❌ Произошла ошибка при добавлении администратора.")
        await state.finish()

async def remove_admin_prompt(message: types.Message) -> None:
    """
    Запрашивает ID администратора для удаления.
    
    Args:
        message: Объект сообщения
    """
    user_id = message.from_user.id
    if not db.is_main_admin(user_id):
        await message.answer("У вас нет прав для удаления администраторов.")
        return
    
    admins = db.get_admins()
    if not admins:
        await message.answer("Список администраторов пуст.")
        return
    
    keyboard = get_admin_remove_keyboard(admins)
    await message.answer(
        "Выберите администратора для удаления:",
        reply_markup=keyboard
    )

async def process_admin_remove(callback: types.CallbackQuery) -> None:
    """
    Обрабатывает удаление администратора.
    
    Args:
        callback: Объект callback-запроса
    """
    try:
        admin_id = int(callback.data.split('_')[-1])
        # Проверяем, не пытаемся ли удалить главного администратора
        if db.is_main_admin(admin_id):
            await callback.answer("❌ Нельзя удалить главного администратора!")
            return
        
        # Удаляем администратора
        if db.remove_admin(admin_id):
            await callback.message.edit_text("✅ Администратор успешно удален!")
        else:
            await callback.message.edit_text("❌ Администратор не найден.")
        
        # Возвращаемся в меню администратора
        keyboard = get_admin_keyboard()
        await callback.message.answer(
            "🌟 *Добро пожаловать в центр управления успехом!* 🌟\n\n"
            "*Наш Божественный Админ*, ваша энергия и лидерство — настоящий двигатель этого проекта! 🚀\n"
            "Вы не просто управляете процессами — вы вдохновляете!\n\n"
            "*Сегодня снова ваш день творить великие перемены!* 🔥",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        await callback.answer("❌ Произошла ошибка при удалении администратора.")

async def back_to_admin(callback: types.CallbackQuery) -> None:
    """
    Возвращает в главное меню администратора.
    
    Args:
        callback: Объект callback-запроса
    """
    keyboard = get_admin_keyboard()
    await callback.message.edit_text(
        "🌟 *Добро пожаловать в центр управления успехом!* 🌟\n\n"
        "*Наш Божественный Админ*, ваша энергия и лидерство — настоящий двигатель этого проекта! 🚀\n"
        "Вы не просто управляете процессами — вы вдохновляете!\n\n"
        "*Сегодня снова ваш день творить великие перемены!* 🔥",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def show_admin_panel(message: types.Message) -> None:
    """
    Показывает админ-панель.
    
    Args:
        message: Объект сообщения
    """
    try:
        await message.answer(
            "👋 Добро пожаловать в админ-панель!\n\n"
            "Выберите действие:",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при показе админ-панели: {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=ReplyKeyboardRemove()
        )

async def handle_back_to_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает возврат в админ-панель.
    
    Args:
        callback: Объект callback-запроса
        state: Состояние FSM
    """
    try:
        await state.finish()
        await callback.message.edit_text(
            "👋 Добро пожаловать в админ-панель!\n\n"
            "Выберите действие:",
            reply_markup=get_admin_keyboard()
        )
        await AdminStates.admin_panel.set()
    except Exception as e:
        logger.error(f"Ошибка при возврате в админ-панель: {str(e)}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_stats_button(message: types.Message) -> None:
    """
    Обрабатывает нажатие на кнопку "Статистика".
    
    Args:
        message: Объект сообщения
    """
    try:
        # Получаем статистику
        total_users = db.get_total_users()
        active_users = db.get_active_users()
        total_referrals = db.get_total_referrals()
        
        # Формируем текст сообщения
        text = (
            "📊 *Статистика бота*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"🟢 Активных пользователей: {active_users}\n"
            f"📈 Всего рефералов: {total_referrals}\n\n"
            "Выберите действие:"
        )
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки 'Статистика': {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_admin_keyboard()
        )

async def edit_levels(message: types.Message) -> None:
    """
    Показывает меню редактирования уровней.
    
    Args:
        message: Объект сообщения
    """
    try:
        keyboard = get_levels_keyboard()
        await message.answer(
            "📊 *Редактирование уровней*\n\n"
            "Выберите уровень для редактирования:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при показе меню редактирования уровней: {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_admin_keyboard()
        )

async def edit_levels_menu(message: types.Message) -> None:
    """
    Показывает меню редактирования уровней.
    
    Args:
        message: Объект сообщения
    """
    try:
        keyboard = get_levels_keyboard()
        await message.answer(
            "📊 *Редактирование уровней*\n\n"
            "Выберите уровень для редактирования:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при показе меню редактирования уровней: {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_admin_keyboard()
        )

async def handle_level_edit(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает запрос на редактирование уровня.
    
    Args:
        callback: Объект callback-запроса
        state: Состояние FSM
    """
    try:
        # Получаем номер уровня из callback_data
        level = int(callback.data.split('_')[-1])
        
        # Получаем текущего предустановленного пользователя для этого уровня
        preset_user = db.get_preset_user_by_level(level)
        if not preset_user:
            await callback.answer("Ошибка: предустановленный пользователь не найден")
            return
            
        # Сохраняем уровень в состоянии
        await state.update_data(level=level)
        
        # Показываем сообщение с текущим номером и запрашиваем новый
        await callback.message.edit_text(
            f"📱 *Редактирование уровня {level}*\n\n"
            f"Текущий номер телефона: `{preset_user.phone_number}`\n\n"
            "Введите новый номер телефона:",
            parse_mode="Markdown",
            reply_markup=get_confirm_keyboard()
        )
        
        # Устанавливаем состояние ожидания нового номера
        await AdminStates.waiting_for_level_data.set()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса на редактирование уровня: {str(e)}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_confirm_level_change(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает подтверждение изменения номера телефона уровня.
    
    Args:
        callback: Объект callback-запроса
        state: Состояние FSM
    """
    try:
        # Получаем сохраненные данные
        data = await state.get_data()
        level = data.get('level')
        new_phone = data.get('new_phone')
        
        if not level or not new_phone:
            await callback.answer("Ошибка: данные не найдены")
            return
            
        # Обновляем номер телефона в БД
        preset_user = db.get_preset_user_by_level(level)
        if preset_user:
            preset_user.phone_number = new_phone
            if db.update_preset_user(preset_user):
                await callback.message.edit_text(
                    f"✅ Номер телефона для уровня {level} успешно обновлен на `{new_phone}`",
                    parse_mode="Markdown"
                )
            else:
                await callback.answer("Ошибка при обновлении номера телефона")
        else:
            await callback.answer("Ошибка: предустановленный пользователь не найден")
            
        # Возвращаемся в админ-панель
        await state.finish()
        await AdminStates.admin_panel.set()
        
    except Exception as e:
        logger.error(f"Ошибка при подтверждении изменения номера телефона: {str(e)}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_cancel_level_change(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает отмену изменения номера телефона уровня.
    
    Args:
        callback: Объект callback-запроса
        state: Состояние FSM
    """
    try:
        await callback.message.edit_text("❌ Изменение номера телефона отменено")
        await state.finish()
        await AdminStates.admin_panel.set()
    except Exception as e:
        logger.error(f"Ошибка при отмене изменения номера телефона: {str(e)}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_level_phone_input(message: types.Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод нового номера телефона для уровня.
    
    Args:
        message: Объект сообщения
        state: Состояние FSM
    """
    try:
        # Проверяем формат номера телефона
        phone = message.text.strip()
        if not phone.startswith('+') or not phone[1:].isdigit():
            await message.answer(
                "❌ Неверный формат номера телефона. Номер должен начинаться с '+' и содержать только цифры.\n"
                "Пожалуйста, введите номер в формате +7XXXXXXXXXX:"
            )
            return
            
        # Проверяем уникальность номера телефона
        existing_user = db.get_preset_user_by_phone(phone)
        if existing_user:
            data = await state.get_data()
            level = data.get('level')
            if existing_user.level != level:
                await message.answer(
                    f"❌ Этот номер телефона уже используется для уровня {existing_user.level}.\n"
                    "Пожалуйста, введите другой номер:"
                )
                return
            
        # Сохраняем новый номер в состоянии
        await state.update_data(new_phone=phone)
        
        # Показываем подтверждение
        data = await state.get_data()
        level = data.get('level')
        
        await message.answer(
            f"📱 *Подтверждение изменения*\n\n"
            f"Уровень: {level}\n"
            f"Новый номер телефона: `{phone}`\n\n"
            "Подтвердите изменение:",
            parse_mode="Markdown",
            reply_markup=get_confirm_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ввода номера телефона: {str(e)}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_admin_keyboard()
        )
        await state.finish()
        await AdminStates.admin_panel.set()

def register_admin_handlers(dp: Dispatcher) -> None:
    """
    Регистрирует обработчики для административных команд.
    
    Args:
        dp: Диспетчер бота
    """
    # Регистрация обработчиков кнопок
    dp.register_message_handler(show_admins_list, lambda msg: msg.text == "👥 Список Админов", state=AdminStates.admin_panel)
    dp.register_message_handler(add_admin_prompt, lambda msg: msg.text == "➕ Добавить Админ", state=AdminStates.admin_panel)
    dp.register_message_handler(remove_admin_prompt, lambda msg: msg.text == "➖ Удалить Админ", state=AdminStates.admin_panel)
    dp.register_message_handler(edit_levels, lambda msg: msg.text == "✏️ Уровни", state=AdminStates.admin_panel)
    dp.register_message_handler(edit_levels_menu, lambda msg: msg.text == "📝 Редактировать Уровни", state=AdminStates.admin_panel)
    dp.register_message_handler(handle_back_to_admin, lambda msg: msg.text == "🔙 Назад", state=AdminStates.admin_panel)
    
    # Регистрация обработчиков callback-запросов
    dp.register_callback_query_handler(
        handle_back_to_admin,
        lambda c: c.data == "back_to_admin",
        state="*"
    )
    
    # Обработчики для статистики
    dp.register_message_handler(
        handle_stats_button,
        lambda m: m.text == "📊 Статистика",
        state=AdminStates.admin_panel
    )

    # Обработчик для ввода ID нового администратора
    dp.register_message_handler(
        process_admin_id,
        state=AdminStates.waiting_for_admin_id
    )

    # Регистрация обработчиков для редактирования уровней
    dp.register_callback_query_handler(
        handle_level_edit,
        lambda c: c.data.startswith("edit_level_"),
        state=AdminStates.waiting_for_level_edit
    )

    # Регистрация обработчиков для подтверждения/отмены
    dp.register_callback_query_handler(
        handle_confirm_level_change,
        lambda c: c.data == "confirm_level_change",
        state=AdminStates.waiting_for_level_data
    )
    dp.register_callback_query_handler(
        handle_cancel_level_change,
        lambda c: c.data == "cancel_level_change",
        state=AdminStates.waiting_for_level_data
    )

    # Регистрация обработчика ввода номера телефона
    dp.register_message_handler(
        handle_level_phone_input,
        state=AdminStates.waiting_for_level_data
    ) 