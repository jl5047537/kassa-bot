import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
from bot.database import db

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

# Клавиатуры
def get_main_keyboard():
    """Возвращает основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("💳 Оплатить участие"))
    keyboard.add(KeyboardButton("👤 Мой профиль"))
    keyboard.add(KeyboardButton("📱 Контакты"))
    return keyboard

def get_registration_keyboard():
    # Возвращаем пустую клавиатуру, чтобы не мешать сценарию
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    return keyboard

# Обработчики команд
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    args = message.get_args()
    referrer_id = args if args else None

    await message.answer(
        "🚀 Добро пожаловать!\nТвой путь к финансовой свободе начинается здесь!\nПройди короткую регистрацию в нашей *Кассе Взаимопомощи* и начни строить своё уверенное будущее уже сегодня. 🔥\nГотов? Жми кнопку ниже! 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            KeyboardButton("🔑 ЗАРЕГИСТРИРОВАТЬСЯ 🔑", request_contact=True)
        )
    )

    if referrer_id:
        await UserStates.waiting_for_phone.set()
        await state.update_data(referrer_id=referrer_id)
    else:
        await UserStates.waiting_for_phone.set()

@dp.callback_query_handler(lambda c: c.data == 'register', state='*')
async def process_register_callback(callback_query: CallbackQuery):
    reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reg_keyboard.add(KeyboardButton("📱 Отправить номер телефона", request_contact=True))
    await callback_query.message.answer(
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить свой номер телефона для регистрации:",
        reply_markup=reg_keyboard
    )
    await callback_query.answer("Кнопка нажата!")

@dp.message_handler(lambda message: message.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    user = db.get_user(str(message.from_user.id))
    if not user:
        await message.answer(
            "Для начала работы необходимо поделиться номером телефона:",
            reply_markup=get_registration_keyboard()
        )
        await UserStates.waiting_for_phone.set()
        return

    await message.answer(
        f"👤 Ваш профиль:\n"
        f"📱 Телефон: {user['phone_number']}\n"
        f"📊 Уровень: {user['level']}"
    )

@dp.message_handler(content_types=['contact'], state=UserStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    
    # Получаем данные из состояния
    state_data = await state.get_data()
    referrer_id = state_data.get('referrer_id')
    
    # Создаем нового пользователя с реферером
    success = db.create_user(
        telegram_id=str(message.from_user.id),
        referrer_id=referrer_id,
        phone_number=phone_number
    )
    
    if success:
        await state.finish()
        await message.answer(
            "Спасибо! Ваш номер телефона успешно сохранен.",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже."
        )

@dp.message_handler(lambda message: message.text == "📱 Контакты")
async def show_contacts(message: types.Message):
    contacts_text = (
        "📱 Контакты для связи:\n\n"
        "👨‍💼 Техническая поддержка: @support\n"
        "📧 Email: support@example.com"
    )
    await message.answer(contacts_text)

@dp.message_handler(lambda message: message.text == "💳 Оплатить участие")
async def process_payment(message: types.Message):
    # Создаем inline-кнопку для сохранения номера
    save_button = InlineKeyboardButton(
        "💾 Сохранить номер",
        url="tg://addcontact?phone=9250007755&name=MATRIX"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.add(save_button)
    
    # Отправляем сообщение с номером телефона
    await message.answer(
        "Для оплаты участия используйте следующий номер телефона:\n"
        "MATRIX: 9250007755\n\n"
        "Вы можете сохранить его в записной книжке:",
        reply_markup=keyboard
    ) 