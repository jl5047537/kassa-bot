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
                    DROP TABLE IF EXISTS payments;
                    DROP TABLE IF EXISTS users;
                """)
                
                # Создаем таблицу users
                cur.execute("""
                    CREATE TABLE users (
                        telegram_id TEXT PRIMARY KEY,
                        level INTEGER DEFAULT 1,
                        referrer_id TEXT,
                        phone_number TEXT,
                        ton_address TEXT,
                        registration_timestamp INTEGER
                    )
                """)
                
                # Создаем таблицу payments
                cur.execute("""
                    CREATE TABLE payments (
                        user_id TEXT,
                        level INTEGER,
                        transaction_hash TEXT,
                        PRIMARY KEY (user_id, level)
                    )
                """)
                
                # Добавляем предустановленных пользователей
                preset_users = [
                    ("79363030567", 4, "79363030567", "0QCT_wLTE_UC29vMlAMsXbjKfGIWvpmdmRZ_ChfPmA6KoWxt"),
                    ("79683327001", 3, "79683327001", "0QCZBUZX-u0GA0ryae-6r4yS0TfJSuA7EutuwSgSLs6_8wIB"),
                    ("79684286626", 2, "79684286626", "0QBbEep4YB5I7MB_6gAfplVR79wvUG8emX5xeuZU5G-z3N8o"),
                    ("79253498238", 1, "79253498238", "0QBrhBVaCW2xresjfQZAaLmuOJGcbPSgLmYzqUcdoF_juPiZ")
                ]
                
                for telegram_id, level, phone, address in preset_users:
                    cur.execute("""
                        INSERT INTO users (telegram_id, level, phone_number, ton_address)
                        VALUES (%s, %s, %s, %s)
                    """, (telegram_id, level, phone, address))
                
                conn.commit()
        logger.info("Таблицы пересозданы и инициализированы")

    def get_user(self, telegram_id: str) -> Optional[dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
                result = cur.fetchone()
                return dict(result) if result else None

    def create_user(self, telegram_id: str, referrer_id: Optional[str] = None, 
                   phone_number: Optional[str] = None, ton_address: Optional[str] = None) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (telegram_id, referrer_id, phone_number, ton_address, registration_timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (telegram_id, referrer_id, phone_number, ton_address, int(time.time())))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка создания пользователя {telegram_id}: {e}")
            return False

    def update_user(self, telegram_id: str, **kwargs) -> bool:
        if not kwargs:
            logger.warning(f"Попытка обновления пользователя {telegram_id} без параметров")
            return False
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    set_clause = ", ".join(f"{k} = %s" for k in kwargs.keys())
                    values = list(kwargs.values()) + [telegram_id]
                    logger.info(f"Обновление пользователя {telegram_id} с параметрами: {kwargs}")
                    cur.execute(f"""
                        UPDATE users SET {set_clause}
                        WHERE telegram_id = %s
                    """, values)
                    conn.commit()
                    logger.info(f"Пользователь {telegram_id} успешно обновлен")
                    return True
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {telegram_id}: {e}")
            return False

    def get_recipients(self) -> List[Tuple[str, int, str]]:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT phone_number, level, ton_address 
                    FROM users 
                    WHERE level BETWEEN 1 AND 4
                """)
                return cur.fetchall()

    def check_payment(self, user_id: str, level: int) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT transaction_hash 
                    FROM payments 
                    WHERE user_id = %s AND level = %s
                """, (user_id, level))
                return cur.fetchone() is not None

    def add_payment(self, user_id: str, level: int, transaction_hash: str) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO payments (user_id, level, transaction_hash)
                        VALUES (%s, %s, %s)
                    """, (user_id, level, transaction_hash))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка добавления платежа для {user_id}: {e}")
            return False

# Создаем экземпляр базы данных
db = Database() 