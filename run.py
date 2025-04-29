import os
from bot.main import dp

# Загружаем переменные окружения
with open('config.env', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True) 