"""
Скрипт для обновления структуры таблицы users.
Добавляет необходимые колонки и изменяет существующие.
"""

import psycopg2
from bot.core.config import settings
import logging
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_users_table():
    """Обновляет структуру таблицы users."""
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB
    )
    
    try:
        with conn.cursor() as cur:
            # Добавляем недостающие колонки
            logger.info("Добавляем недостающие колонки...")
            
            # Добавляем referrer_id если его нет
            cur.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'referrer_id'
                    ) THEN
                        ALTER TABLE users ADD COLUMN referrer_id VARCHAR(50);
                    END IF;
                END $$;
            """)
            
            # Добавляем mentor_id если его нет
            cur.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'mentor_id'
                    ) THEN
                        ALTER TABLE users ADD COLUMN mentor_id INTEGER REFERENCES users(id);
                    END IF;
                END $$;
            """)
            
            # Изменяем типы существующих колонок
            logger.info("Изменяем типы существующих колонок...")
            cur.execute("""
                ALTER TABLE users 
                ALTER COLUMN username TYPE VARCHAR(100),
                ALTER COLUMN first_name TYPE VARCHAR(100),
                ALTER COLUMN last_name TYPE VARCHAR(100);
            """)
            
            # Создаем индексы если их нет
            logger.info("Создаем индексы...")
            cur.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM pg_indexes 
                        WHERE tablename = 'users' 
                        AND indexname = 'idx_users_level'
                    ) THEN
                        CREATE INDEX idx_users_level ON users(level);
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM pg_indexes 
                        WHERE tablename = 'users' 
                        AND indexname = 'idx_users_mentor_id'
                    ) THEN
                        CREATE INDEX idx_users_mentor_id ON users(mentor_id);
                    END IF;
                END $$;
            """)
            
            conn.commit()
            logger.info("Структура таблицы users успешно обновлена")
            
            # Выводим текущую структуру таблицы
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """)
            
            logger.info("\nТекущая структура таблицы users:")
            for row in cur.fetchall():
                logger.info(f"Колонка: {row[0]}, Тип: {row[1]}")
                
    except Exception as e:
        logger.error(f"Ошибка при обновлении таблицы: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_users_table() 