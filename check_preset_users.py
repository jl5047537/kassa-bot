from sqlalchemy import create_engine, text

# Создаем подключение к БД
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/kassa_bot_test"
engine = create_engine(DATABASE_URL)

try:
    # Проверяем данные
    with engine.connect() as conn:
        result = conn.execute(text("SELECT level, phone_number, is_active, mentor_id FROM preset_users ORDER BY level"))
        rows = result.fetchall()
        
        if not rows:
            print("Таблица preset_users пуста")
        else:
            print("Данные в таблице preset_users:")
            for row in rows:
                print(f"Уровень: {row[0]}, Телефон: {row[1]}, Активен: {row[2]}, Наставник: {row[3]}")
            
except Exception as e:
    print(f"Ошибка при проверке данных: {str(e)}") 