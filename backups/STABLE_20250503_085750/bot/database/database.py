"""
Модуль для работы с базой данных.
"""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from .sql_models import Base, User, Referral, create_tables
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
                    phone_number=user.phone_number,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    level=user.level,
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
                phone_number=user.phone_number,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                level=user.level,
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

# Создаем экземпляр базы данных
db = Database() 