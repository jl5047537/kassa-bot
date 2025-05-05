"""
Скрипт для создания базы данных.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from bot.core.config import settings
from bot.database.sql_models import init_db

def get_postgres_url(database="postgres"):
    """Формирование URL подключения к PostgreSQL"""
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{database}"

def drop_database():
    """Удаление базы данных."""
    conn = psycopg2.connect(get_postgres_url())
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    try:
        # Закрываем все активные подключения к базе данных
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}'
            AND pid <> pg_backend_pid();
        """)
        
        # Удаляем базу данных
        cursor.execute(f"DROP DATABASE IF EXISTS {settings.POSTGRES_DB}")
        print(f"База данных {settings.POSTGRES_DB} успешно удалена")
        return True
    
    except Exception as e:
        print(f"Ошибка при удалении базы данных: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def create_database():
    """Создание и инициализация базы данных."""
    # Создаем базу данных
    conn = psycopg2.connect(get_postgres_url())
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'CREATE DATABASE {settings.POSTGRES_DB}')
        print(f"База данных {settings.POSTGRES_DB} успешно создана")
        
        # Закрываем соединение с postgres
        cursor.close()
        conn.close()
        
        # Создаем engine для новой базы данных
        engine = create_engine(get_postgres_url(settings.POSTGRES_DB))
        
        # Инициализируем структуру базы данных
        if init_db(engine):
            print("База данных успешно инициализирована")
            return True
        return False
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        return False
    
    finally:
        if not cursor.closed:
            cursor.close()
        if not conn.closed:
            conn.close()

if __name__ == "__main__":
    if drop_database():
        create_database() 