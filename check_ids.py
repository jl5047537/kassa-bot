from sqlalchemy import create_engine, text

# Создаем подключение к базе данных
engine = create_engine('postgresql://postgres:postgres123@localhost:5432/kassa_bot_test')

# Проверяем ID в обеих таблицах
with engine.connect() as conn:
    print("\nID в таблице admins:")
    result = conn.execute(text("SELECT id, telegram_id, username, is_main FROM admins ORDER BY id"))
    for row in result:
        print(f"ID: {row[0]}, Telegram ID: {row[1]}, Username: {row[2]}, Главный: {row[3]}")
    
    print("\nID в таблице preset_users:")
    result = conn.execute(text("SELECT id, level, username, mentor_id FROM preset_users ORDER BY id"))
    for row in result:
        print(f"ID: {row[0]}, Уровень: {row[1]}, Username: {row[2]}, Наставник: {row[3]}") 