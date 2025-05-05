from sqlalchemy import create_engine, text
from bot.database.sql_models import Base, Admin

# Создаем подключение к базе данных
engine = create_engine('postgresql://postgres:postgres123@localhost:5432/kassa_bot_test')

# Проверяем данные в таблице admins
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, telegram_id, username, first_name, last_name, is_main, phone_number FROM admins"))
    print("\nТекущие данные в таблице admins:")
    for row in result:
        print(f"ID: {row[0]}, Telegram ID: {row[1]}, Username: {row[2]}, "
              f"Имя: {row[3]}, Фамилия: {row[4]}, Главный: {row[5]}, Телефон: {row[6]}") 