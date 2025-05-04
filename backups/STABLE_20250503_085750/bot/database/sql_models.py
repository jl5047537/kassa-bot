"""
Модуль с SQLAlchemy моделями базы данных.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, MetaData, Table, inspect, text, create_engine, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Создаем метаданные
metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Log(Base):
    """
    Модель для хранения логов в базе данных.
    
    Attributes:
        id: Уникальный идентификатор
        timestamp: Время создания записи
        level: Уровень логирования
        logger_name: Имя логгера
        message: Текст сообщения
        module: Имя модуля
        function: Имя функции
        line: Номер строки
        extra_data: Дополнительные данные в JSON формате
        process_id: ID процесса
        thread_id: ID потока
    """
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(10), index=True)
    logger_name = Column(String(100), index=True)
    message = Column(Text)
    module = Column(String(100))
    function = Column(String(100))
    line = Column(Integer)
    extra_data = Column(Text)  # JSON строка с дополнительными данными
    process_id = Column(Integer)
    thread_id = Column(Integer)
    
    # Создаем составной индекс для частых запросов
    __table_args__ = (
        Index('idx_logs_timestamp_level', 'timestamp', 'level'),
        Index('idx_logs_logger_name_timestamp', 'logger_name', 'timestamp'),
    )

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    level = Column(Integer, default=0)
    referrer_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Определяем отношения
    referrals_made = relationship(
        'Referral',
        foreign_keys='Referral.referrer_id',
        backref='referrer',
        cascade='all, delete-orphan'
    )
    referrals_received = relationship(
        'Referral',
        foreign_keys='Referral.referred_id',
        backref='referred',
        cascade='all, delete-orphan'
    )

class Referral(Base):
    """Модель реферала."""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('users.id'))
    referred_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables(engine):
    """Создает все таблицы в базе данных."""
    Base.metadata.create_all(engine)

def init_db(engine):
    """
    Инициализация базы данных с проверкой соединения
    """
    try:
        # Проверяем соединение
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Соединение с базой данных установлено успешно")
        
        # Создаем таблицы
        create_tables(engine)
        print("Структура базы данных создана успешно")
        
        return True
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False 