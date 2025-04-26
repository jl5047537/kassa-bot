# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extras import DictCursor
import logging
from typing import Optional, List, Tuple
import json
import time
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Загружаем переменные окружения
        with open('config.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

        self.conn_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres123'),
            'dbname': os.getenv('POSTGRES_DB', 'kassa_bot'),
            'client_encoding': 'utf8'
        }
        self.recreate_tables()

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def recreate_tables(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Удаляем существующие таблицы
                cur.execute("""
                    DROP TABLE IF EXISTS users;
                """)
                
                # Создаем таблицу users
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        telegram_id TEXT UNIQUE,
                        level INTEGER DEFAULT 1,
                        phone_number TEXT,
                        referrer_id TEXT,
                        created_at INTEGER
                    )
                """)
                
                # Добавляем предустановленных пользователей
                preset_users = [
                    ("79363030567", 4, "79363030567", None),
                    ("79683327001", 3, "79683327001", None),
                    ("79684286626", 2, "79684286626", None),
                    ("79253498238", 1, "79253498238", None)
                ]
                
                for telegram_id, level, phone, referrer in preset_users:
                    cur.execute("""
                        INSERT INTO users (telegram_id, level, phone_number, referrer_id)
                        VALUES (%s, %s, %s, %s)
                    """, (telegram_id, level, phone, referrer))
                
                conn.commit()
        logger.info("Таблицы пересозданы и инициализированы")

    def get_user(self, telegram_id: str) -> Optional[dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
                result = cur.fetchone()
                return dict(result) if result else None

    def create_user(self, telegram_id: str, referrer_id: Optional[str] = None, 
                   phone_number: Optional[str] = None, level: int = 0) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (telegram_id, referrer_id, phone_number, level, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (telegram_id, referrer_id, phone_number, level, int(time.time())))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {telegram_id}: {e}")
            return False

    def update_user(self, telegram_id: str, phone_number: Optional[str] = None) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users 
                        SET phone_number = %s
                        WHERE telegram_id = %s
                    """, (phone_number, telegram_id))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {telegram_id}: {e}")
            return False

    def get_recipients(self) -> List[Tuple[str, int]]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT phone_number, level 
                    FROM users 
                    WHERE level BETWEEN 1 AND 4
                """)
                return cur.fetchall()

# Создаем экземпляр базы данных
db = Database() 