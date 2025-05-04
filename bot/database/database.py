"""
Модуль для работы с базой данных.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from .sql_models import Base, User, Referral, Admin, PresetUser, create_tables
from ..core.config import settings, DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    """
    Класс для работы с базой данных.
    """
    
    def __init__(self):
        """
        Инициализация подключения к базе данных.
        """
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # Создаем таблицы, если они не существуют
        try:
            create_tables(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Модель пользователя или None
        """
        session = self.Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return User(
                    id=user.id,
                    telegram_id=user.telegram_id,
                    phone_number=user.phone_number,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    level=user.level,
                    mentor_id=user.mentor_id,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
            return None
        finally:
            session.close()
    
    def create_user(self, user: User) -> User:
        """
        Создание нового пользователя.
        
        Args:
            user: Модель пользователя
            
        Returns:
            User: Созданная модель пользователя
        """
        session = self.Session()
        try:
            db_user = User(
                id=user.id,
                telegram_id=user.telegram_id,
                phone_number=user.phone_number,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                level=user.level,
                mentor_id=user.mentor_id,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            session.add(db_user)
            session.commit()
            return user
        finally:
            session.close()
    
    def get_referrals_count(self, referrer_id: int) -> int:
        """
        Получение количества рефералов пользователя.
        
        Args:
            referrer_id: ID пользователя
            
        Returns:
            int: Количество рефералов
        """
        session = self.Session()
        try:
            return session.query(Referral).filter(Referral.referrer_id == referrer_id).count()
        finally:
            session.close()
    
    def create_referral(self, referrer_id: int, referred_id: int) -> Referral:
        """
        Создание реферальной связи.
        
        Args:
            referrer_id: ID пригласившего пользователя
            referred_id: ID приглашенного пользователя
            
        Returns:
            Referral: Созданная модель реферальной связи
        """
        session = self.Session()
        try:
            db_referral = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id
            )
            session.add(db_referral)
            session.commit()
            return Referral(
                id=db_referral.id,
                referrer_id=db_referral.referrer_id,
                referred_id=db_referral.referred_id,
                created_at=db_referral.created_at
            )
        finally:
            session.close()

    def is_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если пользователь администратор, иначе False
        """
        session = self.Session()
        try:
            admin = session.query(Admin).filter(Admin.telegram_id == str(user_id)).first()
            return admin is not None
        finally:
            session.close()

    def is_main_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь главным администратором.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если пользователь главный администратор, иначе False
        """
        session = self.Session()
        try:
            admin = session.query(Admin).filter(
                Admin.telegram_id == str(user_id),
                Admin.is_main == True
            ).first()
            return admin is not None
        finally:
            session.close()

    def get_admins(self) -> List[Admin]:
        """
        Получает список всех администраторов.
        
        Returns:
            List[Admin]: Список администраторов
        """
        session = self.Session()
        try:
            return session.query(Admin).all()
        finally:
            session.close()

    def add_admin(self, user_id: int, username: str, first_name: str, last_name: str, is_main: bool = False) -> Optional[Admin]:
        """
        Добавляет нового администратора.
        
        Args:
            user_id: ID пользователя в Telegram
            username: Username пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            is_main: Является ли главным администратором
            
        Returns:
            Optional[Admin]: Модель администратора или None в случае ошибки
        """
        session = self.Session()
        try:
            # Проверяем, не существует ли уже администратор
            existing_admin = session.query(Admin).filter(Admin.telegram_id == str(user_id)).first()
            if existing_admin:
                return None
            
            # Создаем нового администратора
            admin = Admin(
                telegram_id=str(user_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_main=is_main
            )
            session.add(admin)
            session.commit()
            return admin
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def remove_admin(self, user_id: int) -> bool:
        """
        Удаляет администратора.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            bool: True если удаление успешно, иначе False
        """
        session = self.Session()
        try:
            admin = session.query(Admin).filter(Admin.telegram_id == str(user_id)).first()
            if not admin:
                return False
            
            # Нельзя удалить главного администратора
            if admin.is_main:
                return False
            
            session.delete(admin)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_preset_user_by_level(self, level: int) -> Optional[PresetUser]:
        """
        Получает предустановленного пользователя по уровню.
        
        Args:
            level: Уровень пользователя
            
        Returns:
            Optional[PresetUser]: Пользователь или None, если не найден
        """
        try:
            return self.Session().query(PresetUser).filter(PresetUser.level == level).first()
        except Exception as e:
            logger.error(f"Ошибка при получении предустановленного пользователя по уровню {level}: {str(e)}")
            return None

    def get_preset_user_by_phone(self, phone_number: str) -> Optional[PresetUser]:
        """
        Получает предустановленного пользователя по номеру телефона.
        
        Args:
            phone_number: Номер телефона
            
        Returns:
            Optional[PresetUser]: Пользователь или None, если не найден
        """
        try:
            return self.Session().query(PresetUser).filter(PresetUser.phone_number == phone_number).first()
        except Exception as e:
            logger.error(f"Ошибка при получении предустановленного пользователя по номеру {phone_number}: {str(e)}")
            return None

    def get_preset_users(self) -> List[PresetUser]:
        """
        Получает список предустановленных пользователей.
        
        Returns:
            List[PresetUser]: Список предустановленных пользователей
        """
        try:
            return self.Session().query(PresetUser).filter(PresetUser.level.in_([1, 2, 3, 4])).order_by(PresetUser.level).all()
        except Exception as e:
            logger.error(f"Ошибка при получении предустановленных пользователей: {str(e)}")
            return []

    def update_preset_user(self, user: PresetUser) -> bool:
        """
        Обновляет данные предустановленного пользователя.
        
        Args:
            user: Объект предустановленного пользователя
            
        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            self.Session().merge(user)
            self.Session().commit()
            logger.info(f"Данные предустановленного пользователя уровня {user.level} успешно обновлены")
            return True
        except Exception as e:
            self.Session().rollback()
            logger.error(f"Ошибка при обновлении данных предустановленного пользователя: {str(e)}")
            return False

    def get_user_by_level(self, level: int) -> Optional[User]:
        """
        Получает пользователя по уровню.
        
        Args:
            level: Уровень пользователя
            
        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        try:
            return self.Session().query(User).filter(User.level == level).first()
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по уровню {level}: {str(e)}")
            return None

    def add_user(self, user: User) -> Optional[User]:
        """
        Добавляет нового пользователя в базу данных.
        
        Args:
            user: Объект пользователя
            
        Returns:
            Optional[User]: Добавленный пользователь или None в случае ошибки
        """
        try:
            # Проверяем, существует ли пользователь
            existing_user = self.Session().query(User).filter(User.telegram_id == user.telegram_id).first()
            if existing_user:
                logger.warning(f"Пользователь с telegram_id {user.telegram_id} уже существует")
                return existing_user
            
            # Добавляем пользователя
            self.Session().add(user)
            self.Session().commit()
            logger.info(f"Пользователь {user.telegram_id} успешно добавлен")
            return user
        except Exception as e:
            self.Session().rollback()
            logger.error(f"Ошибка при добавлении пользователя: {str(e)}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Получает пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        try:
            return self.Session().query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по ID {user_id}: {str(e)}")
            return None

    def update_user(self, user: User) -> bool:
        """
        Обновляет данные пользователя.
        
        Args:
            user: Объект пользователя с обновленными данными
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            self.Session().merge(user)
            self.Session().commit()
            logger.info(f"Данные пользователя {user.telegram_id} успешно обновлены")
            return True
        except Exception as e:
            self.Session().rollback()
            logger.error(f"Ошибка при обновлении данных пользователя: {str(e)}")
            return False

# Создаем экземпляр базы данных
db = Database() 