import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.core.config import settings

async def start(update, context):
    await update.message.reply_text(
        "Привет! Я бот для управления кассой. "
        "Я помогу вам следить за транзакциями и рефералами."
    )

async def help(update, context):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/balance - Показать баланс\n"
        "/transactions - История транзакций\n"
        "/referrals - Управление рефералами"
    )

def main():
    # Создаем приложение
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main() 