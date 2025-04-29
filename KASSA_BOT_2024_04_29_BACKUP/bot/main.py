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
def get_main_keyboard(user_id: str = None):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    if user_id:
        user = db.get_user(user_id)
        if user and user.get('level', 0) > 0:
            # Для активных пользователей (уровень > 0)
            keyboard.add(KeyboardButton("👥 Пригласить Друзей"))
            keyboard.add(KeyboardButton("📊 Профиль"))
            keyboard.add(KeyboardButton("❓ Помощь"))
        else:
            # Для неактивных пользователей
            keyboard.add(KeyboardButton("🔑 Стартовый Ключ"))
            keyboard.add(KeyboardButton("📊 Профиль"), KeyboardButton("❓ Помощь"))
    else:
        # Если user_id не указан, показываем базовые кнопки
        keyboard.add(KeyboardButton("🔑 Стартовый Ключ"))
        keyboard.add(KeyboardButton("📊 Профиль"), KeyboardButton("❓ Помощь"))
    
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

def get_admin_keyboard():
    """Возвращает клавиатуру для администратора"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Список Администраторов"))
    keyboard.add(KeyboardButton("➕ Добавить Админа"))
    keyboard.add(KeyboardButton("➖ Удалить Админа"))
    return keyboard

# Обработчики команд
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    # Получаем данные пользователя
    user_id = str(message.from_user.id)
    username = message.from_user.username
    
    logger.info(f"User started bot: id={user_id}, username={username}")
    
    # Проверяем, является ли пользователь администратором
    is_admin = db.is_admin(str(message.from_user.id))
    is_main_admin = db.is_main_admin(str(message.from_user.id))
    
    logger.info(f"Admin check results: is_admin={is_admin}, is_main_admin={is_main_admin}")
    
    if is_admin or is_main_admin:
        # Создаем клавиатуру администратора
        keyboard = get_admin_keyboard()
        
        # Отправляем приветственное сообщение с клавиатурой
        await message.answer(
            "🌟 *Добро пожаловать в центр управления успехом!* 🌟\n\n"
            "*Наш Божественный Админ*, ваша энергия и лидерство — настоящий двигатель этого проекта! 🚀\n"
            "Вы не просто управляете процессами — вы вдохновляете!\n\n"
            "*Сегодня снова ваш день творить великие перемены!* 🔥",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

    # Если не администратор - показываем обычное меню
    args = message.get_args()
    if args:  # Если есть реферальный ID
        await state.set_state(UserStates.waiting_for_phone.state)
        await state.update_data(referrer_id=args)
        logger.info(f"Saved referrer_id: {args} for user {user_id}")
    else:
        await state.set_state(UserStates.waiting_for_phone.state)
        logger.info(f"No referrer_id for user {user_id}")

    await message.answer(
        "🚀 *Добро пожаловать!*\n"
        "Твой путь к финансовой свободе начинается здесь!\n"
        "Пройди короткую регистрацию в нашей *Кассе Взаимопомощи* и начни строить своё уверенное будущее уже сегодня. 🔥\n"
        "Готов? Жми кнопку ниже! 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            KeyboardButton("🔑 Зарегистрироваться 🔑", request_contact=True)
        )
    )

@dp.callback_query_handler(lambda c: c.data == 'register', state='*')
async def process_register_callback(callback_query: CallbackQuery):
    reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reg_keyboard.add(KeyboardButton("📱 Отправить номер телефона", request_contact=True))
    await callback_query.message.answer(
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить свой номер телефона для регистрации:",
        reply_markup=reg_keyboard
    )
    await callback_query.answer("Кнопка нажата!")

@dp.message_handler(lambda message: message.text == "📊 Профиль")
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
    referrals_count = db.get_referrals_count(str(message.from_user.id))
    current_level = user.get('level', 0)

    # Формируем текст с уровнями и прогрессом
    levels_text = ""
    level_requirements = {
        4: 4,    # Начинающий
        3: 16,   # Продвинутый
        2: 64,   # Профессионал
        1: 256   # Эксперт
    }
    
    for level in range(4, 0, -1):
        required_referrals = level_requirements[level]
        is_current = level == current_level
        is_completed = level < current_level
        is_locked = level > current_level
        
        level_emoji = "✅" if is_completed else "🔒" if is_locked else "🏆" if is_current else "🏃"
        level_status = " (Текущий)" if is_current else " (Заблокирован)" if is_locked else " (Завершен)" if is_completed else ""
        
        progress = f"{referrals_count}/{required_referrals}" if not is_completed else "✅"
        
        levels_text += f"{level_emoji} {level} уровень {level_status} - {progress}\n"

    profile_text = (
        f"👤 *Ваш профиль*\n\n"
        f"📱 Телефон: {user['phone_number']}\n"
        f"🆔 Ваш referral ID: *{ref_id}*\n"
        f"👥 Приглашено друзей: *{referrals_count}*\n\n"
        f"*Уровни:*\n{levels_text}"
    )

    await message.answer(
        profile_text,
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=['contact'], state=UserStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    user_id = str(message.from_user.id)
    
    # Получаем данные из состояния
    state_data = await state.get_data()
    referrer_id = state_data.get('referrer_id')
    
    # Проверяем, существует ли пользователь
    existing_user = db.get_user(user_id)
    if existing_user:
        # Формируем сообщение о текущем статусе
        referrals_count = db.get_referrals_count(user_id)
        current_level = existing_user.get('level', 0)
        
        status_text = (
            f"Вы уже зарегистрированы в системе!\n\n"
            f"Ваш текущий статус:\n"
            f"• Уровень: {current_level}\n"
            f"• Рефералов: {referrals_count}\n"
            f"• Статус оплаты: {'✅ Оплачено' if current_level > 0 else '❌ Не оплачено'}\n\n"
        )
        
        if current_level == 0:
            status_text += "Для активации нажмите кнопку '🔑 Стартовый Ключ'"
        else:
            status_text += "Вы можете приглашать друзей и получать бонусы!"
        
        await state.finish()
        await message.answer(
            status_text,
            reply_markup=get_main_keyboard(user_id)
        )
        return
    
    # Если пользователь не существует, создаем новую запись
    success = db.create_user(
        telegram_id=user_id,
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
            reply_markup=get_main_keyboard(user_id)
        )
    else:
        await message.answer(
            "Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже."
        )

@dp.message_handler(lambda message: message.text == "❓ Помощь")
async def show_contacts(message: types.Message):
    contacts_text = (
        "📱 Контакты для связи:\n\n"
        "👨‍💼 Техническая поддержка: @support\n"
        "📧 Email: support@example.com"
    )
    await message.answer(contacts_text)

@dp.message_handler(lambda message: message.text == "🔑 Стартовый Ключ")
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
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_payment:{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_payment:{user_id}")
    )
    
    # Формируем сообщение для администраторов
    admin_message = (
        f"🔔 Новый платеж!\n"
        f"Пользователь ID: {user_id}\n"
        f"Телефон: {user['phone_number']}\n"
        f"Сумма: 4 TON\n\n"
        f"Пожалуйста, проверьте свой кошелек и подтвердите или отклоните платеж"
    )
    
    # Получаем список активных администраторов
    admins = db.get_active_admins()
    sent_to_admins = False
    
    # Отправляем сообщение каждому администратору
    for admin in admins:
        try:
            await bot.send_message(
                chat_id=admin['telegram_id'],
                text=admin_message,
                reply_markup=confirm_keyboard
            )
            sent_to_admins = True
            logger.info(f"Сообщение отправлено администратору {admin['telegram_id']}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения администратору {admin['telegram_id']}: {e}")
    
    if not sent_to_admins:
        await callback_query.message.answer(
            "Произошла ошибка при отправке уведомления администраторам. Пожалуйста, попробуйте позже."
        )
        await callback_query.answer()
        return
    
    # Отправляем сообщение пользователю
    await callback_query.message.answer(
        "Ваш платеж отправлен на проверку. Пожалуйста, подождите подтверждения.",
        reply_markup=None
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith(('confirm_payment:', 'reject_payment:')))
async def process_payment_action(callback_query: CallbackQuery):
    """Обработчик подтверждения/отклонения платежа"""
    if not db.is_admin(str(callback_query.from_user.id)):
        await callback_query.answer("У вас нет прав администратора")
        return

    action, user_id = callback_query.data.split(':')
    user = db.get_user(user_id)
    
    if not user:
        await callback_query.message.answer("Ошибка: пользователь не найден")
        await callback_query.answer()
        return

    admin_id = str(callback_query.from_user.id)
    if action == 'confirm_payment':
        # Обновляем уровень пользователя в базе данных
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET level = 1
                    WHERE telegram_id = %s
                """, (user_id,))
                conn.commit()
        
        # Отправляем сообщение пользователю с обновленной клавиатурой
        await bot.send_message(
            chat_id=user_id,
            text="✅ Ваш платеж подтвержден! Спасибо за оплату.\n\n"
                 "Теперь вы можете приглашать друзей и получать бонусы!",
            reply_markup=get_main_keyboard(user_id)
        )
        
        # Обновляем сообщение администратора
        await callback_query.message.edit_text(
            f"✅ Платеж подтвержден администратором {admin_id}"
        )
    else:
        # Отправляем сообщение пользователю об отклонении платежа
        await bot.send_message(
            chat_id=user_id,
            text="❌ Ваш платеж отклонен. Пожалуйста, проверьте сумму и получателя платежа.",
            reply_markup=get_main_keyboard(user_id)
        )
        
        # Обновляем сообщение администратора
        await callback_query.message.edit_text(
            f"❌ Платеж отклонен администратором {admin_id}"
        )
    
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

async def check_and_update_level(user_id: str):
    user = db.get_user(user_id)
    if not user:
        return

    current_level = user.get('level', 0)
    referrals_count = db.get_referrals_count(user_id)
    
    # Проверяем, достиг ли пользователь следующего уровня
    next_level = current_level + 1
    required_referrals = {
        4: 4,    # Начинающий
        3: 16,   # Продвинутый
        2: 64,   # Профессионал
        1: 256   # Эксперт
    }.get(next_level, 0)
    
    if referrals_count >= required_referrals and next_level <= 4:
        db.update_user_level(user_id, next_level)
        return True
    return False

@dp.message_handler(lambda message: message.text == "👥 Пригласить Друзей")
async def invite_friends(message: types.Message):
    user = db.get_user(str(message.from_user.id))
    if not user:
        await message.answer(
            "Для начала работы зарегистрируйтесь:",
            reply_markup=get_registration_keyboard()
        )
        await UserStates.waiting_for_phone.set()
        return

    ref_id = get_referral_id(user['phone_number'])
    
    # Получаем username бота
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Создаем inline-кнопку для шаринга
    share_button = InlineKeyboardButton(
        "👥 Поделиться",
        switch_inline_query=f"Присоединяйся к Кассе Взаимопомощи! https://t.me/{bot_username}?start={ref_id}"
    )
    share_keyboard = InlineKeyboardMarkup()
    share_keyboard.add(share_button)
    
    invite_text = (
        f"🎯 *Пригласи друзей и получи бонусы!*\n\n"
        f"Твой referral ID: *{ref_id}*\n\n"
        f"*Как пригласить друзей:*\n"
        f"1️⃣ Отправь своему другу эту ссылку:\n"
        f"https://t.me/{bot_username}?start={ref_id}\n\n"
        f"*За каждого приглашенного друга ты получишь бонусы!* 🎁"
    )

    # Отправляем сообщение с кнопкой шаринга
    await message.answer(
        invite_text,
        parse_mode="Markdown",
        reply_markup=share_keyboard
    )

    # Проверяем и обновляем уровень после приглашения
    if await check_and_update_level(str(message.from_user.id)):
        await message.answer(
            "🎉 Поздравляем! Вы достигли нового уровня!",
            reply_markup=get_main_keyboard()
        )

@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    """Обработчик выбора контакта"""
    if message.contact:
        # Возвращаем основное меню
        await message.answer(
            "Отлично! Теперь отправьте вашему другу сообщение с реферальным ID.",
            reply_markup=get_main_keyboard()
        )

# Команды администратора
@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    """Показывает панель администратора"""
    if not db.is_admin(str(message.from_user.id)):
        await message.answer("У вас нет прав администратора.")
        return

    is_main = db.is_main_admin(str(message.from_user.id))
    welcome_text = "👋 Добро пожаловать в панель администратора!\n\n"
    if is_main:
        welcome_text += "👑 Вы главный администратор\n\n"
    else:
        welcome_text += "👤 Вы администратор\n\n"
    
    welcome_text += "📋 Доступные команды:\n"
    welcome_text += "• /admin - показать это сообщение\n"
    welcome_text += "• /admins - показать список администраторов\n"
    
    if is_main:
        welcome_text += "• /add_admin ID - добавить администратора\n"
        welcome_text += "• /remove_admin ID - удалить администратора\n"
    
    # Создаем клавиатуру администратора
    keyboard = get_admin_keyboard()
    
    # Отправляем сообщение с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "👥 Список Администраторов")
async def show_admins_list(message: types.Message):
    """Показывает список администраторов"""
    if not db.is_admin(str(message.from_user.id)):
        await message.answer("У вас нет прав администратора.")
        return

    admins = db.get_active_admins()
    if not admins:
        await message.answer("Список администраторов пуст.")
        return

    admin_list = ["👥 Список администраторов:"]
    for admin in admins:
        prefix = "👑" if admin['is_main_admin'] else "👤"
        admin_info = f"{prefix} {admin['first_name']} {admin['last_name']} (@{admin['username']})"
        if admin['is_main_admin']:
            admin_info += " - Главный администратор"
        admin_list.append(admin_info)

    await message.answer("\n".join(admin_list))

@dp.message_handler(lambda message: message.text == "➕ Добавить Админа")
async def add_admin_prompt(message: types.Message):
    """Запрашивает ID нового администратора"""
    if not db.is_main_admin(str(message.from_user.id)):
        await message.answer("Только главный администратор может добавлять новых администраторов.")
        return

    await message.answer(
        "Введите ID пользователя, которого хотите сделать администратором.\n"
        "Пример: 123456789"
    )

@dp.message_handler(lambda message: message.text == "➖ Удалить Админа")
async def remove_admin_prompt(message: types.Message):
    """Запрашивает ID администратора для удаления"""
    if not db.is_main_admin(str(message.from_user.id)):
        await message.answer("Только главный администратор может удалять администраторов.")
        return

    await message.answer(
        "Введите ID администратора, которого хотите удалить.\n"
        "Пример: 123456789"
    )

@dp.message_handler(commands=['admins'])
async def cmd_list_admins(message: types.Message):
    """Показывает список администраторов"""
    if not db.is_admin(str(message.from_user.id)):
        await message.answer("У вас нет прав администратора.")
        return

    admins = db.get_active_admins()
    if not admins:
        await message.answer("Список администраторов пуст.")
        return

    admin_list = ["👥 Список администраторов:"]
    for admin in admins:
        prefix = "👑" if admin['is_main_admin'] else "👤"
        admin_info = f"{prefix} {admin['first_name']} {admin['last_name']} (@{admin['username']})"
        if admin['is_main_admin']:
            admin_info += " - Главный администратор"
        admin_list.append(admin_info)

    await message.answer("\n".join(admin_list))

@dp.message_handler(commands=['add_admin'])
async def cmd_add_admin(message: types.Message):
    """Добавляет нового администратора"""
    if not db.is_main_admin(str(message.from_user.id)):
        await message.answer("Только главный администратор может добавлять новых администраторов.")
        return

    args = message.get_args()
    if not args:
        await message.answer("Укажите ID администратора.\nПример: /add_admin 123456789")
        return

    admin_id = args.strip()
    if not admin_id.isdigit():
        await message.answer("ID администратора должен быть числом.")
        return

    if db.add_admin(admin_id, str(message.from_user.id)):
        await message.answer(f"✅ Администратор {admin_id} успешно добавлен.")
    else:
        await message.answer(f"❌ Не удалось добавить администратора {admin_id}.")

@dp.message_handler(commands=['remove_admin'])
async def cmd_remove_admin(message: types.Message):
    """Удаляет администратора"""
    if not db.is_main_admin(str(message.from_user.id)):
        await message.answer("Только главный администратор может удалять администраторов.")
        return

    args = message.get_args()
    if not args:
        await message.answer("Укажите ID администратора.\nПример: /remove_admin 123456789")
        return

    admin_id = args.strip()
    if not admin_id.isdigit():
        await message.answer("ID администратора должен быть числом.")
        return

    if admin_id == os.getenv('MAIN_ADMIN_ID'):
        await message.answer("❌ Нельзя удалить главного администратора.")
        return

    if db.remove_admin(admin_id, str(message.from_user.id)):
        await message.answer(f"✅ Администратор {admin_id} успешно удален.")
    else:
        await message.answer(f"❌ Не удалось удалить администратора {admin_id}.") 