"""
Скрипт для просмотра всех таблиц в базе данных.
"""

from sqlalchemy import create_engine, text, inspect
from bot.core.config import settings

# Создаем подключение к БД
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

def print_table_data(table_name: str):
    """Выводит содержимое таблицы."""
    print(f"\n{'='*20} Таблица {table_name} {'='*20}")
    try:
        with engine.connect() as conn:
            # Получаем информацию о столбцах
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            print("\nСтруктура таблицы:")
            for row in result:
                print(f"  {row[0]}: {row[1]}")
            
            # Получаем данные
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            print("\nДанные:")
            rows = result.fetchall()
            if not rows:
                print("  Таблица пуста")
            else:
                for row in rows:
                    print(f"  {row}")
    except Exception as e:
        print(f"Ошибка при получении данных таблицы {table_name}: {str(e)}")

try:
    # Получаем список всех таблиц
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    print(f"\nНайдено таблиц: {len(table_names)}")
    for table_name in table_names:
        print_table_data(table_name)
            
except Exception as e:
    print(f"Ошибка при получении списка таблиц: {str(e)}") 