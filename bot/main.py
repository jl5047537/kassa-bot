import logging
import os
import hashlib
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
    keyboard.add(KeyboardButton("🔑 Стартовый ключ 🔑"))
    keyboard.add(KeyboardButton("👤 Мой профиль"))
    keyboard.add(KeyboardButton("📱 Контакты"))
    keyboard.add(KeyboardButton("💎 Запустить Бот ТГ Кошелька"))
    return keyboard

def get_registration_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔑 Зарегистрироваться", request_contact=True))
    return keyboard

def get_referral_id(phone_number):
    if not phone_number:
        return "нет данных"
    phone_bytes = phone_number.encode('utf-8')
    hash_object = hashlib.md5(phone_bytes)
    hash_hex = hash_object.hexdigest()
    return hash_hex[:8]

# Обработчики команд
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    args = message.get_args()
    referrer_id = args if args else None

    await message.answer(
        "🚀 *Добро пожаловать!*\n"
        "Твой путь к финансовой свободе начинается здесь!\n"
        "Пройди короткую регистрацию в нашей *Кассе Взаимопомощи* и начни строить своё уверенное будущее уже сегодня. 🔥\n"
        "Готов? Жми кнопку ниже! 👇",
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
            "Для начала работы зарегистрируйтесь:",
            reply_markup=get_registration_keyboard()
        )
        await UserStates.waiting_for_phone.set()
        return
    ref_id = get_referral_id(user['phone_number'])
    levels_text = (
        "🏃 0 уровень ✅\n"
        "🥉 4 уровень\n"
        "🥈 3 уровень\n"
        "🥇 2 уровень\n"
        "🏆 1 уровень"
    )
    await message.answer(
        f"👤 Ваш профиль:\n"
        f"📱 Телефон: {user['phone_number']}\n"
        f"🆔 Ваш referral ID: {ref_id}\n"
        f"{levels_text}"
    )

@dp.message_handler(content_types=['contact'], state=UserStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    
    # Получаем данные из состояния
    state_data = await state.get_data()
    referrer_id = state_data.get('referrer_id')
    
    # Создаем нового пользователя с реферером и уровнем 0
    success = db.create_user(
        telegram_id=str(message.from_user.id),
        referrer_id=referrer_id,
        phone_number=phone_number,
        level=0
    )
    
    if success:
        await state.finish()
        await message.answer(
            "*🎉 Ура, ты с нами!*\n"
            "Поздравляем с регистрацией в *Кассе Взаимопомощи*! 🎊\n\n"
            "Остался последний лёгкий шаг — нажми на *🔑 Стартовый ключ 🔑* и активируй своё участие.\n"
            "Это разовый символический взнос в 4 TON, который не только откроет тебе путь к стабильности, финансовой свободе и уверенности в завтрашнем дне, 💸 но и поможет всей системе работать честно, надёжно и исправно для каждого участника. 🔗\n\n"
            "*Готов начать? Жми на кнопку и стартуем вместе! 🚀*",
            parse_mode="Markdown",
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

@dp.message_handler(lambda message: message.text == "🔑 Стартовый ключ 🔑")
async def process_payment(message: types.Message):
    save_button = InlineKeyboardButton(
        "💾 Сохранить Контакт",
        url="tg://addcontact?phone=9684286626&name=Стартовый_Ключ"
    )
    confirm_button = InlineKeyboardButton(
        "✅ Я сохранил",
        callback_data="saved_contact"
    )
    trouble_button = InlineKeyboardButton(
        "🤔 Упс, проблема",
        callback_data="trouble"
    )
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(save_button)
    keyboard.row(confirm_button, trouble_button)
    await message.answer(
        "🚀 Следуй инструкциям бота, привлекай друзей и начни строить своё будущее прямо сейчас!\n"
        "*Вперёд к новым возможностям!* 🔥\n\n"
        "*Чтобы оплатить разовый взнос БЕЗ КОМИССИИ Телеграм тебе нужно сохранить Контакт для оплаты в телефоне*\n\n"
        "👆 Нажми на кнопку ниже — откроется записная книжка.\n\n"
        "💾 Сохрани в ней предложенный Контакт.\n"
        "📤 Когда сохранишь, нажми кнопку 'Я сохранил' и следуй дальнейшим инструкциям.\n"
        
        "*Готов? Жми кнопку и действуй! 🔥*",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'saved_contact')
async def process_saved_contact(callback_query: CallbackQuery):
    pay_keyboard = InlineKeyboardMarkup()
    pay_keyboard.add(InlineKeyboardButton("💎 Запустить Бот ТГ Кошелька", url="https://t.me/wallet"))
    pay_keyboard.add(
        InlineKeyboardButton("✅ Я оплатил", callback_data="paid"),
        InlineKeyboardButton("🤔 Упс, проблема", callback_data="trouble")
    )
    await callback_query.message.answer(
        "💳 Открой свой кошелёк в Telegram.\n"
        "📤 Нажми кнопку 'Отправить', выбери сохранённый контакт из записной книжки.\n"
        "💸 Переведи 4 TON для активации участия.\n\n"
        "📤 После оплаты нажми здесь кнопку 'Я оплатил'\n"
        "Бот пришлет подтверждение и активирует участие\n\n",
        reply_markup=pay_keyboard
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'paid')
async def process_paid(callback_query: CallbackQuery):
    """Обработчик нажатия кнопки 'Я оплатил'"""
    # Получаем информацию о пользователе
    user_id = str(callback_query.from_user.id)
    user = db.get_user(user_id)
    
    if not user:
        await callback_query.message.answer("Ошибка: пользователь не найден")
        await callback_query.answer()
        return
    
    # Создаем клавиатуру для подтверждения/отклонения
    confirm_keyboard = InlineKeyboardMarkup()
    confirm_keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_payment"),
        InlineKeyboardButton("❌ Отклонить", callback_data="reject_payment")
    )
    
    # Формируем сообщение для администратора
    admin_message = (
        f"🔔 Новый платеж!\n"
        f"Пользователь ID: {user_id}\n"
        f"Телефон: {user['phone_number']}\n"
        f"Сумма: 4 TON\n\n"
        f"Пожалуйста, проверьте свой кошелек и подтвердите или отклоните платеж"
    )
    
    # Отправляем сообщение администратору
    admin_username = "@DeeNastiya"
    try:
        await bot.send_message(
            chat_id=admin_username,
            text=admin_message,
            reply_markup=confirm_keyboard
        )
        logger.info(f"Сообщение отправлено администратору {admin_username}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")
        await callback_query.message.answer(
            "Произошла ошибка при отправке уведомления администратору. Пожалуйста, попробуйте позже."
        )
    
    # Отправляем сообщение пользователю
    await callback_query.message.answer(
        "Ваш платеж отправлен на проверку. Пожалуйста, подождите подтверждения.",
        reply_markup=confirm_keyboard
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'confirm_payment')
async def confirm_payment(callback_query: CallbackQuery):
    """Обработчик подтверждения платежа"""
    # Здесь будет логика подтверждения платежа
    await callback_query.message.answer("Платеж подтвержден!")
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'reject_payment')
async def reject_payment(callback_query: CallbackQuery):
    """Обработчик отклонения платежа"""
    # Здесь будет логика отклонения платежа
    await callback_query.message.answer("Платеж отклонен!")
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'trouble')
async def process_trouble(callback_query: CallbackQuery):
    await callback_query.message.answer("Если возникли трудности, напишите в поддержку: @support")
    await callback_query.answer()

@dp.message_handler(lambda message: message.text == "💎 Запустить Бот ТГ Кошелька")
async def open_wallet(message: types.Message):
    """Обработчик для открытия кошелька"""
    # Создаем кнопку с URL для открытия бота кошелька
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "💎 Запустить Бот ТГ Кошелька",
        url="https://t.me/wallet"
    ))
    
    # Отправляем сообщение с инструкцией
    await message.answer(
        "Для открытия кошелька нажмите на кнопку ниже:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "open_wallet")
async def process_wallet_callback(callback_query: types.CallbackQuery):
    """Обработчик нажатия на кнопку открытия кошелька"""
    await callback_query.message.answer("Пожалуйста, используйте команду /wallet в любом чате для открытия кошелька.")
    await callback_query.answer() 