import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from bot.database import db
import asyncio
import json
import time

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния FSM
class UserStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_ton_address = State()
    waiting_for_transaction_hash = State()

# Клавиатуры
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("💳 Оплатить"))
    keyboard.add(KeyboardButton("👤 Мой профиль"))
    keyboard.add(KeyboardButton("📱 Контакты"))
    return keyboard

def get_payment_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Оплатить", callback_data="pay"))
    return keyboard

# Обработчики команд
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user = db.get_user(str(message.from_user.id))
    if not user:
        # Создаем нового пользователя
        referrer_id = None
        if len(message.text.split()) > 1:
            referrer_id = message.text.split()[1]
        
        db.create_user(
            telegram_id=str(message.from_user.id),
            referrer_id=referrer_id
        )
        
        # Создаем клавиатуру с кнопкой для отправки номера телефона
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("📱 Отправить номер телефона", request_contact=True))
        
        await message.answer(
            "👋 Добро пожаловать! Для начала работы, пожалуйста, поделитесь своим номером телефона.",
            reply_markup=keyboard
        )
        await UserStates.waiting_for_phone.set()
    else:
        await message.answer(
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )

@dp.message_handler(content_types=types.ContentType.CONTACT, state=UserStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Получен контакт от пользователя {message.from_user.id}")
        phone = message.contact.phone_number
        logger.info(f"Номер телефона: {phone}")
        
        # Очищаем номер от всех нецифровых символов
        phone = ''.join(filter(str.isdigit, phone))
        if not phone.startswith('7'):
            phone = '7' + phone
        
        logger.info(f"Обработанный номер: {phone}")
        
        # Обновляем данные пользователя
        success = db.update_user(str(message.from_user.id), phone_number=phone)
        logger.info(f"Обновление номера телефона: {'успешно' if success else 'ошибка'}")
        
        if success:
            await message.answer(
                "Отлично! Теперь введите ваш TON кошелек:",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Назад"))
            )
            await UserStates.waiting_for_ton_address.set()
        else:
            await message.answer(
                "Произошла ошибка при сохранении номера телефона. Пожалуйста, попробуйте еще раз.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton("📱 Поделиться номером", request_contact=True)]],
                    resize_keyboard=True
                )
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке номера телефона: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton("📱 Поделиться номером", request_contact=True)]],
                resize_keyboard=True
            )
        )

@dp.message_handler(state=UserStates.waiting_for_ton_address)
async def process_ton_address(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer(
            "Пожалуйста, поделитесь своим номером телефона.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton("📱 Поделиться номером", request_contact=True)]],
                resize_keyboard=True
            )
        )
        await UserStates.waiting_for_phone.set()
        return
    
    ton_address = message.text
    db.update_user(str(message.from_user.id), ton_address=ton_address)
    
    await state.finish()
    await message.answer(
        "Регистрация завершена! Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message_handler(lambda message: message.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user = db.get_user(str(message.from_user.id))
    if not user:
        await message.answer("Вы не зарегистрированы. Нажмите /start")
        return
    
    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"📱 Телефон: {user['phone_number']}\n"
        f"💰 TON кошелек: {user['ton_address']}\n"
        f"📊 Уровень: {user['level']}\n"
    )
    
    await message.answer(profile_text)

@dp.message_handler(lambda message: message.text == "💳 Оплатить")
async def process_payment(message: types.Message):
    user = db.get_user(str(message.from_user.id))
    if not user:
        await message.answer("Вы не зарегистрированы. Нажмите /start")
        return
    
    if user['level'] >= 4:
        await message.answer("Вы уже достигли максимального уровня!")
        return
    
    next_level = user['level'] + 1
    payment_amount = 100 * next_level  # Пример расчета суммы
    
    await message.answer(
        f"Для перехода на уровень {next_level} необходимо оплатить {payment_amount} TON.\n\n"
        f"После оплаты отправьте хеш транзакции.",
        reply_markup=get_payment_keyboard()
    )
    await UserStates.waiting_for_transaction_hash.set()

@dp.message_handler(state=UserStates.waiting_for_transaction_hash)
async def process_transaction_hash(message: types.Message, state: FSMContext):
    user = db.get_user(str(message.from_user.id))
    if not user:
        await state.finish()
        await message.answer("Вы не зарегистрированы. Нажмите /start")
        return
    
    transaction_hash = message.text
    next_level = user['level'] + 1
    
    if db.add_payment(str(message.from_user.id), next_level, transaction_hash):
        db.update_user(str(message.from_user.id), level=next_level)
        await message.answer(
            f"Поздравляем! Вы перешли на уровень {next_level}!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Ошибка при обработке платежа. Пожалуйста, попробуйте еще раз."
        )
    
    await state.finish()

@dp.message_handler(lambda message: message.text == "📱 Контакты")
async def show_contacts(message: types.Message):
    contacts_text = (
        "📱 Контакты для связи:\n\n"
        "👨‍💼 Техническая поддержка: @support\n"
        "📧 Email: support@example.com"
    )
    await message.answer(contacts_text) 