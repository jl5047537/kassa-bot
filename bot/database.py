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
                    DROP TABLE IF EXISTS admins;
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
                
                # Создаем таблицу admins
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id SERIAL PRIMARY KEY,
                        telegram_id TEXT UNIQUE,
                        is_main_admin BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
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
                
                # Добавляем главного администратора
                main_admin_id = os.getenv('MAIN_ADMIN_ID')
                if main_admin_id:
                    logger.info(f"Adding main admin with ID: {main_admin_id}")
                    
                    # Сначала удаляем старую запись если она есть
                    cur.execute("""
                        DELETE FROM admins WHERE telegram_id = %s
                    """, (main_admin_id,))
                    
                    # Добавляем новую запись
                    cur.execute("""
                        INSERT INTO admins (telegram_id, is_main_admin, is_active, created_at)
                        VALUES (%s, TRUE, TRUE, %s)
                        RETURNING id
                    """, (main_admin_id, int(time.time())))
                    
                    result = cur.fetchone()
                    logger.info(f"Main admin record after insert: {result}")
                    conn.commit()
                    
                    if result:
                        logger.info("Main admin added successfully")
                    else:
                        logger.error("Failed to add main admin")
                
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

    def is_admin(self, telegram_id: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        if not telegram_id:
            return False
            
        logger.info(f"Checking admin status for telegram_id: {telegram_id}")
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT is_active FROM admins 
                    WHERE telegram_id = %s AND is_active = TRUE
                """, (telegram_id,))
                result = cur.fetchone()
                logger.info(f"Admin check result: {result}")
                return bool(result)

    def is_main_admin(self, telegram_id: str) -> bool:
        """Проверяет, является ли пользователь главным администратором"""
        if not telegram_id:
            return False
            
        logger.info(f"Checking main admin status for telegram_id: {telegram_id}")
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT is_main_admin FROM admins 
                    WHERE telegram_id = %s 
                    AND is_main_admin = TRUE 
                    AND is_active = TRUE
                """, (telegram_id,))
                result = cur.fetchone()
                logger.info(f"Main admin check result: {result}")
                return bool(result)

    def add_admin(self, telegram_id: str, added_by: str) -> bool:
        """Добавляет нового администратора"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO admins (telegram_id, created_at)
                        VALUES (%s, %s)
                        ON CONFLICT (telegram_id) 
                        DO UPDATE SET is_active = TRUE
                        RETURNING id
                    """, (telegram_id, int(time.time())))
                    conn.commit()
                    return bool(cur.fetchone())
        except Exception as e:
            logger.error(f"Ошибка добавления администратора {telegram_id}: {e}")
            return False

    def remove_admin(self, telegram_id: str, removed_by: str) -> bool:
        """Деактивирует администратора"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE admins 
                        SET is_active = FALSE
                        WHERE telegram_id = %s AND is_main_admin = FALSE
                        RETURNING id
                    """, (telegram_id,))
                    conn.commit()
                    return bool(cur.fetchone())
        except Exception as e:
            logger.error(f"Ошибка удаления администратора {telegram_id}: {e}")
            return False

    def get_active_admins(self) -> List[dict]:
        """Возвращает список активных администраторов"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT telegram_id, is_main_admin 
                    FROM admins 
                    WHERE is_active = TRUE
                    ORDER BY is_main_admin DESC, telegram_id
                """)
                return [dict(row) for row in cur.fetchall()]

    def update_user_status(self, telegram_id: str, status: str) -> bool:
        """Обновляет статус пользователя"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users 
                        SET level = %s
                        WHERE telegram_id = %s
                    """, (1 if status == 'active' else 0, telegram_id))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка обновления статуса пользователя {telegram_id}: {e}")
            return False

    def update_user_level(self, telegram_id: str, new_level: int) -> bool:
        """Обновляет уровень пользователя"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users 
                        SET level = %s
                        WHERE telegram_id = %s
                    """, (new_level, telegram_id))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Ошибка обновления уровня пользователя {telegram_id}: {e}")
            return False

    def get_referrals_count(self, telegram_id: str) -> int:
        """Возвращает количество рефералов пользователя"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE referrer_id = %s
                """, (telegram_id,))
                result = cur.fetchone()
                return result[0] if result else 0

# Создаем экземпляр базы данных
db = Database() 