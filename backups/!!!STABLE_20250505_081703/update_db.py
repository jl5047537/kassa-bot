"""
Скрипт для обновления базы данных.
"""

from sqlalchemy import create_engine, text
from bot.core.config import settings

# Создаем подключение к БД
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

# SQL-запросы для обновления структуры и данных
sql_commands = """
-- Добавляем недостающие поля в таблицу preset_users
ALTER TABLE preset_users 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Очищаем таблицу
TRUNCATE TABLE preset_users;

-- Добавляем предустановленных пользователей без mentor_id
INSERT INTO preset_users (level, phone_number, is_active) VALUES
(1, '79683327001', true),
(2, '79684286626', true),
(3, '79253498238', true),
(4, '79363030567', true);

-- Обновляем mentor_id после добавления всех пользователей
UPDATE preset_users SET mentor_id = NULL WHERE level = 1;
UPDATE preset_users SET mentor_id = (SELECT id FROM preset_users WHERE level = 1) WHERE level = 2;
UPDATE preset_users SET mentor_id = (SELECT id FROM preset_users WHERE level = 2) WHERE level = 3;
UPDATE preset_users SET mentor_id = (SELECT id FROM preset_users WHERE level = 3) WHERE level = 4;

-- Проверяем результат
SELECT level, phone_number, is_active, mentor_id FROM preset_users ORDER BY level;
"""

try:
    # Выполняем SQL-команды
    with engine.connect() as conn:
        conn.execute(text(sql_commands))
        conn.commit()
    
    print("Таблица preset_users успешно обновлена")
    
    # Проверяем результат
    with engine.connect() as conn:
        result = conn.execute(text("SELECT level, phone_number, is_active, mentor_id FROM preset_users ORDER BY level"))
        print("\nТекущие данные в таблице:")
        for row in result:
            print(f"Уровень: {row[0]}, Телефон: {row[1]}, Активен: {row[2]}, Наставник: {row[3]}")
            
except Exception as e:
    print(f"Ошибка при обновлении таблицы: {str(e)}") 