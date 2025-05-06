"""
Скрипт для проверки структуры базы данных.
"""

from sqlalchemy import create_engine, inspect
from bot.core.config import settings

def check_database_structure():
    """Проверка структуры базы данных."""
    try:
        # Создаем подключение
        engine = create_engine(
            f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}'
            f'@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
        )
        
        # Получаем инспектор
        inspector = inspect(engine)
        
        print("Проверка структуры базы данных:")
        print("-" * 50)
        
        # Проверяем таблицы
        tables = inspector.get_table_names()
        print(f"\nНайдено таблиц: {len(tables)}")
        
        for table in tables:
            print(f"\nТаблица: {table}")
            print("Колонки:")
            for column in inspector.get_columns(table):
                print(f"  - {column['name']}: {column['type']}")
            
            # Проверяем индексы
            indexes = inspector.get_indexes(table)
            if indexes:
                print("\nИндексы:")
                for index in indexes:
                    print(f"  - {index['name']}: {index['column_names']}")
            
            # Проверяем внешние ключи
            foreign_keys = inspector.get_foreign_keys(table)
            if foreign_keys:
                print("\nВнешние ключи:")
                for fk in foreign_keys:
                    print(f"  - {fk['referred_table']}.{fk['referred_columns']}")
        
        print("\nПроверка завершена успешно")
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке структуры базы данных: {e}")
        return False

if __name__ == "__main__":
    check_database_structure() 