import sqlite3
import json
import time
import logging
import requests
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Константы
TOKEN = "7844652385:AAGWn0XM3YiJF8hgfQ5yOomT4-sKYGGziuA"  # Замени на свой токен
TON_API_KEY = "2c97cb20ca2b2cb03966f8252eb94d4f9b98ff0d8a253187557119d003d8f868"  # Твой API-ключ TON
USER_CONFIG_FILE = "user_config.json"

# Функция нормализации адреса
def normalize_address(address):
    # Убираем префикс (0Q или EQ) и приводим к нижнему регистру
    if address.startswith("0Q") or address.startswith("EQ"):
        address = address[2:]
    # Заменяем _ на - и убираем лишние различия
    address = address.replace("_", "-").lower()
    return address

# Инициализация базы данных
def init_db():
    with sqlite3.connect("kassa.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id TEXT PRIMARY KEY,
                level INTEGER DEFAULT 1,
                referrer_id TEXT,
                phone_number TEXT,
                ton_address TEXT,
                registration_timestamp INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                user_id TEXT,
                level INTEGER,
                transaction_hash TEXT,
                PRIMARY KEY (user_id, level)
            )
        """)
        # Предустановленные пользователи для уровней
        preset_users = [
            ("79363030567", 4, "+79363030567", "0QCT_wLTE_UC29vMlAMsXbjKfGIWvpmdmRZ_ChfPmA6KoWxt"),
            ("79683327001", 3, "+79683327001", "0QCZBUZX-u0GA0ryae-6r4yS0TfJSuA7EutuwSgSLs6_8wIB"),
            ("79684286626", 2, "+79684286626", "0QBbEep4YB5I7MB_6gAfplVR79wvUG8emX5xeuZU5G-z3N8o"),
            ("79253498238", 1, "+79253498238", "0QBrhBVaCW2xresjfQZAaLmuOJGcbPSgLmYzqUcdoF_juPiZ")
        ]
        for telegram_id, level, phone, address in preset_users:
            c.execute("INSERT OR IGNORE INTO users (telegram_id, level, phone_number, ton_address) VALUES (?, ?, ?, ?)",
                      (telegram_id, level, phone, address))
        conn.commit()
    logging.info("Предустановленные уровни загружены в базу")
    logging.info("База данных инициализирована")

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    try:
        with sqlite3.connect("kassa.db") as conn:
            c = conn.cursor()
            c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
            if c.fetchone():
                await update.message.reply_text("Вы уже зарегистрированы. Используйте /status.")
                return
            referrer_id = context.args[0] if context.args else None
            if referrer_id:
                c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (referrer_id,))
                if not c.fetchone():
                    referrer_id = None

            # Проверяем user_config.json для автозаполнения
            phone_number = None
            ton_address = None
            logging.info(f"Проверяем {USER_CONFIG_FILE} для пользователя {user_id}")
            try:
                with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logging.info(f"Содержимое {USER_CONFIG_FILE}: {json.dumps(config, ensure_ascii=False)}")
                    for user_data in config["users"]:
                        if user_data["telegram_id"] == user_id:
                            phone_number = user_data["phone_number"]
                            ton_address = user_data["ton_address"]
                            normalized_address = normalize_address(ton_address)
                            logging.info(f"Найдены данные для {user_id}: phone={phone_number}, address={ton_address}, нормализованный: {normalized_address}")
                            break
                    else:
                        logging.info(f"Данные для {user_id} не найдены в {USER_CONFIG_FILE}")
            except FileNotFoundError:
                logging.error(f"Файл {USER_CONFIG_FILE} не найден")
            except json.JSONDecodeError as e:
                logging.error(f"Ошибка в формате {USER_CONFIG_FILE}: {e}")

            # Регистрируем пользователя
            c.execute("""
                INSERT INTO users (telegram_id, level, referrer_id, phone_number, ton_address, registration_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, 5, referrer_id, phone_number, ton_address, int(time.time())))
            conn.commit()

        # Формируем ответ
        if phone_number and ton_address:
            await update.message.reply_text(
                f"🎉 Добро пожаловать в \"Касса\", {user_id}!\n"
                f"Телефон: {phone_number}\n"
                f"TON-адрес: {ton_address}\n"
                "Ваши данные подтянуты автоматически. Используйте /pay для старта."
            )
        else:
            await update.message.reply_text(
                "🎉 Добро пожаловать в \"Касса\"!\n1. Укажите /set_phone\n2. Укажите /set_address\n3. Используйте /pay для старта."
            )
        logging.info(f"Зарегистрирован пользователь {user_id}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка регистрации {user_id}: {e}")
        await update.message.reply_text("Ошибка регистрации. Попробуйте позже.")

# Команда /pay
async def pay(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    try:
        with sqlite3.connect("kassa.db") as conn:
            c = conn.cursor()
            c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
            if not c.fetchone():
                await update.message.reply_text("Вы не зарегистрированы. Используйте /start.")
                return

            # Собираем список номеров для оплаты
            c.execute("SELECT phone_number, level, ton_address FROM users WHERE level BETWEEN 1 AND 4")
            recipients = c.fetchall()
            if not recipients:
                await update.message.reply_text("Нет доступных уровней для оплаты.")
                return

            message = "📱 Номера для оплаты (по 1 TON):\n"
            for i, (phone, level, address) in enumerate(recipients, 1):
                message += f"{i}. {phone} (уровень {level}) - {address}\n"
            message += "\nЯ все оплатил /confirm_payment"
            await update.message.reply_text(message)
    except sqlite3.Error as e:
        logging.error(f"Ошибка в /pay для {user_id}: {e}")
        await update.message.reply_text("Ошибка получения списка. Попробуйте позже.")

# Команда /confirm_payment
async def confirm_payment(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    try:
        with sqlite3.connect("kassa.db") as conn:
            c = conn.cursor()
            c.execute("SELECT level FROM users WHERE telegram_id = ?", (user_id,))
            user_level = c.fetchone()
            if not user_level:
                await update.message.reply_text("Вы не зарегистрированы. Используйте /start.")
                return

            unpaid_levels = []
            for level in range(1, 5):
                c.execute("SELECT transaction_hash FROM payments WHERE user_id = ? AND level = ?", (user_id, level))
                if c.fetchone() is None:
                    unpaid_levels.append(level)

            if unpaid_levels:
                await update.message.reply_text(f"Вы не оплатили уровень(и): {', '.join(map(str, unpaid_levels))}")
            else:
                c.execute("UPDATE users SET level = 5 WHERE telegram_id = ?", (user_id,))
                conn.commit()
                await update.message.reply_text("Все оплаты подтверждены! Ваш уровень: 5.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка в confirm_payment для {user_id}: {e}")
        await update.message.reply_text("Ошибка проверки оплаты. Попробуйте позже.")

# Функция мониторинга транзакций
async def monitor_transactions():
    try:
        with sqlite3.connect("kassa.db") as conn:
            c = conn.cursor()
            c.execute("SELECT telegram_id, ton_address FROM users")
            users = c.fetchall()

            for user_id, ton_address in users:
                normalized_user_address = normalize_address(ton_address)
                logging.info(f"Проверяем транзакции для {user_id}, нормализованный адрес: {normalized_user_address}")

                for level in range(1, 5):
                    c.execute("SELECT ton_address FROM users WHERE level = ?", (level,))
                    recipient = c.fetchone()
                    if not recipient:
                        continue
                    recipient_address = recipient[0]

                    # Запрос к API TON
                    url = f"https://testnet.toncenter.com/api/v2/getTransactions?address={recipient_address}&limit=10&api_key={TON_API_KEY}"
                    response = requests.get(url)
                    logging.info(f"Запрос к API: {url}")
                    if response.status_code == 200:
                        logging.info(f"Статус ответа API: 200")
                        data = response.json()
                        logging.info(f"Получен ответ API: {json.dumps(data, ensure_ascii=False)}")
                        for tx in data["result"]:
                            source = tx["in_msg"]["source"]
                            normalized_source = normalize_address(source)
                            value = int(tx["in_msg"]["value"]) / 10**9  # Переводим в TON
                            tx_hash = tx["transaction_id"]["hash"]

                            if normalized_source == normalized_user_address and value >= 1.0:
                                logging.info(f"Входящая транзакция {tx_hash} для {user_id} на уровень {level}")
                                c.execute("SELECT transaction_hash FROM payments WHERE user_id = ? AND level = ?", (user_id, level))
                                if c.fetchone() is None:
                                    c.execute("INSERT INTO payments (user_id, level, transaction_hash) VALUES (?, ?, ?)", (user_id, level, tx_hash))
                                    conn.commit()
                                    logging.info(f"Оплата уровня {level} засчитана для {user_id}")
    except Exception as e:
        logging.error(f"Ошибка в monitor_transactions: {e}")

# Основная асинхронная функция
async def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("confirm_payment", confirm_payment))

    # Настройка планировщика
    scheduler = AsyncIOScheduler()
    scheduler.add_job(monitor_transactions, 'interval', minutes=1)
    scheduler.start()

    # Запуск бота
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logging.info("Бот запущен")

    # Держим цикл событий открытым
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        await app.stop()
        await app.shutdown()
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())