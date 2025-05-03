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
    # Словарь соответствия имен полей
    FIELD_MAPPING = {
        "username": "username",
        "phone": "phone_number",
        "first_name": "first_name",
        "last_name": "last_name"
    }

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
                        first_name TEXT,
                        last_name TEXT,
                        username TEXT,
                        avatar TEXT,
                        user_link TEXT,
                        phone_number TEXT,
                        level INTEGER DEFAULT 0,
                        referrer_id TEXT,
                        created_at INTEGER,
                        updated_at INTEGER
                    )
                """)
                
                # Создаем таблицу admins
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id SERIAL PRIMARY KEY,
                        telegram_id TEXT UNIQUE,
                        first_name TEXT,
                        last_name TEXT,
                        username TEXT,
                        avatar TEXT,
                        user_link TEXT,
                        phone_number TEXT,
                        is_main_admin BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at INTEGER,
                        updated_at INTEGER
                    )
                """)
                
                # Добавляем предустановленных пользователей
                preset_users = [
                    {
                        "telegram_id": "7806482506",
                        "first_name": "LEVEL 1",
                        "last_name": "Alex",
                        "username": "Alex_Level_1",
                        "avatar": None,
                        "user_link": "https://t.me/Alex_Level_1",
                        "phone_number": "9683327001",
                        "level": 1,
                        "referral_id": None,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time())
                    },
                    {
                        "telegram_id": "7355173647",
                        "first_name": "LEVEL 2",
                        "last_name": "Nastyia",
                        "username": "Nastiya_Level_2",
                        "avatar": None,
                        "user_link": "https://t.me/Nastiya_Level_2",
                        "phone_number": "9684286626",
                        "level": 2,
                        "referral_id": None,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time())
                    },
                    {
                        "telegram_id": "7651819044",
                        "first_name": "LEVEL 3",
                        "last_name": "Viktor",
                        "username": "travelercinema",
                        "avatar": None,
                        "user_link": "https://t.me/travelercinema",
                        "phone_number": "9253498238",
                        "level": 3,
                        "referral_id": None,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time())
                    },
                    {
                        "telegram_id": "7694850355",
                        "first_name": "LEVEL 4",
                        "last_name": "Mark",
                        "username": "Mark_Level_4",
                        "avatar": None,
                        "user_link": "https://t.me/Mark_Level_4",
                        "phone_number": "9363030567",
                        "level": 4,
                        "referral_id": None,
                        "created_at": int(time.time()),
                        "updated_at": int(time.time())
                    }
                ]
                
                for user in preset_users:
                    cur.execute("""
                        INSERT INTO users (
                            telegram_id, first_name, last_name, username,
                            avatar, user_link, phone_number, level,
                            referrer_id, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user["telegram_id"],
                        user["first_name"],
                        user["last_name"],
                        user["username"],
                        user["avatar"],
                        user["user_link"],
                        user["phone_number"],
                        user["level"],
                        user["referral_id"],
                        user["created_at"],
                        user["updated_at"]
                    ))
                
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
                        INSERT INTO admins (
                            telegram_id, first_name, last_name, username, 
                            avatar, user_link, phone_number, 
                            is_main_admin, is_active, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        main_admin_id,
                        "Jan",  # first_name
                        "Levy",  # last_name
                        "JanLevy",  # username
                        None,  # avatar
                        "https://t.me/JanLevy",  # user_link
                        "9165047537",  # phone_number
                        True,  # is_main_admin
                        True,  # is_active
                        int(time.time()),  # created_at
                        int(time.time())   # updated_at
                    ))
                    
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

    def update_user(self, telegram_id: str, phone_number: Optional[str] = None, referral_id: Optional[str] = None) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if phone_number and referral_id:
                        cur.execute("""
                            UPDATE users 
                            SET phone_number = %s, referral_id = %s
                            WHERE telegram_id = %s
                        """, (phone_number, referral_id, telegram_id))
                    elif phone_number:
                        cur.execute("""
                            UPDATE users 
                            SET phone_number = %s
                            WHERE telegram_id = %s
                        """, (phone_number, telegram_id))
                    elif referral_id:
                        cur.execute("""
                            UPDATE users 
                            SET referral_id = %s
                            WHERE telegram_id = %s
                        """, (referral_id, telegram_id))
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

    def add_admin(self, telegram_id: str, added_by: str, first_name: str = None, 
                 last_name: str = None, username: str = None, avatar: str = None, 
                 user_link: str = None, phone_number: str = None) -> bool:
        """Добавляет нового администратора"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO admins (
                            telegram_id, first_name, last_name, username,
                            avatar, user_link, phone_number, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (telegram_id) 
                        DO UPDATE SET 
                            first_name = EXCLUDED.first_name,
                            last_name = EXCLUDED.last_name,
                            username = EXCLUDED.username,
                            avatar = EXCLUDED.avatar,
                            user_link = EXCLUDED.user_link,
                            phone_number = EXCLUDED.phone_number,
                            is_active = TRUE,
                            updated_at = EXCLUDED.updated_at
                        RETURNING id
                    """, (
                        telegram_id,
                        first_name,
                        last_name,
                        username,
                        avatar,
                        user_link,
                        phone_number,
                        int(time.time()),
                        int(time.time())
                    ))
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
                    SELECT 
                        telegram_id, first_name, last_name, username,
                        avatar, user_link, phone_number, is_main_admin 
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
            logger.error(f"Error updating user level: {e}")
            return False

    def update_user_field(self, telegram_id: str, field: str, value: str) -> bool:
        """Обновляет указанное поле пользователя"""
        try:
            # Проверяем существование поля в словаре
            if field not in self.FIELD_MAPPING:
                logger.error(f"Поле {field} не найдено в списке допустимых полей")
                return False

            db_field = self.FIELD_MAPPING[field]
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Используем безопасную подстановку параметров
                    cur.execute(f"""
                        UPDATE users 
                        SET {db_field} = %s
                        WHERE telegram_id = %s
                    """, (value, telegram_id))
                    conn.commit()
            
            logger.info(f"Поле {field} успешно обновлено для пользователя {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении поля {field} для пользователя {telegram_id}: {e}")
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

    def get_all_users(self) -> List[dict]:
        """Возвращает список всех пользователей"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT 
                        telegram_id, first_name, last_name, username,
                        level, phone_number, referrer_id, created_at
                    FROM users 
                    ORDER BY level DESC, created_at DESC
                """)
                return [dict(row) for row in cur.fetchall()]

# Создаем экземпляр базы данных
db = Database() 