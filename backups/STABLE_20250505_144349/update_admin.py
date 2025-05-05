"""
Скрипт для обновления таблицы администраторов.
"""

from sqlalchemy import create_engine, text
from bot.core.config import settings

# Создаем подключение к БД
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

# SQL-запросы для обновления структуры и данных
sql_commands = """
-- Добавляем столбец phone_number, если его нет
ALTER TABLE admins 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);

-- Создаем индекс для номера телефона
CREATE INDEX IF NOT EXISTS idx_admin_phone ON admins(phone_number);

-- Добавляем главного администратора
INSERT INTO admins (telegram_id, username, first_name, last_name, phone_number, is_main)
VALUES ('7963523915', 'main_admin', 'Main', 'Admin', '79165047537', true)
ON CONFLICT (telegram_id) DO UPDATE 
SET phone_number = EXCLUDED.phone_number,
    is_main = EXCLUDED.is_main;

-- Проверяем результат
SELECT id, telegram_id, username, first_name, last_name, phone_number, is_main 
FROM admins 
ORDER BY id;
"""

try:
    # Выполняем SQL-команды
    with engine.connect() as conn:
        conn.execute(text(sql_commands))
        conn.commit()
    
    print("Таблица admins успешно обновлена")
    
    # Проверяем результат
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, telegram_id, username, first_name, last_name, phone_number, is_main FROM admins ORDER BY id"))
        print("\nТекущие данные в таблице:")
        for row in result:
            print(f"ID: {row[0]}, Telegram ID: {row[1]}, Username: {row[2]}, Имя: {row[3]}, Фамилия: {row[4]}, Телефон: {row[5]}, Главный: {row[6]}")
            
except Exception as e:
    print(f"Ошибка при обновлении таблицы: {str(e)}") 