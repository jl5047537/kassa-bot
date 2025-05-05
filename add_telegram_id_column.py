from sqlalchemy import create_engine, text

# Создаем подключение к БД
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/kassa_bot_test"
engine = create_engine(DATABASE_URL)

try:
    # Добавляем столбец telegram_id
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(50) UNIQUE;"))
        conn.commit()
        print("Столбец telegram_id успешно добавлен в таблицу users")
        
        # Проверяем структуру таблицы
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';"))
        print("\nТекущая структура таблицы users:")
        for row in result:
            print(f"Столбец: {row[0]}, Тип: {row[1]}")
            
except Exception as e:
    print(f"Ошибка при добавлении столбца: {str(e)}") 