from sqlalchemy import create_engine, text

# Создаем подключение к БД
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/kassa_bot_test"
engine = create_engine(DATABASE_URL)

# SQL-запросы для обновления структуры и данных
sql_commands = """
-- Добавляем столбцы, если их нет
ALTER TABLE preset_users 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Очищаем таблицу
TRUNCATE TABLE preset_users;

-- Добавляем предустановленных пользователей
INSERT INTO preset_users (level, phone_number, is_active, mentor_id) VALUES
(1, '79683327001', true, NULL),
(2, '79684286626', true, 1),
(3, '79253498238', true, 2),
(4, '79363030567', true, 3);
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