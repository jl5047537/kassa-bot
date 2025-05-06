"""
Модуль для записи логов в базу данных.

Этот модуль предоставляет обработчик для записи логов в базу данных PostgreSQL.
Логи записываются асинхронно для минимизации влияния на производительность.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session
from ..database.sql_models import Log
from ..database.database import db

# Создаем пул потоков для асинхронной записи
executor = ThreadPoolExecutor(max_workers=1)

class DatabaseHandler(logging.Handler):
    """
    Обработчик для записи логов в базу данных.
    
    Attributes:
        level: Уровень логирования
        batch_size: Размер пакета для групповой записи
        batch_timeout: Таймаут для записи пакета (в секундах)
    """
    
    def __init__(self, level: int = logging.NOTSET, batch_size: int = 100, batch_timeout: float = 5.0):
        super().__init__(level)
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._buffer = []
        self._last_flush = datetime.now()
        self._lock = asyncio.Lock()
    
    async def _flush_buffer(self) -> None:
        """Асинхронно записывает буфер логов в базу данных."""
        if not self._buffer:
            return
            
        try:
            session: Session = db.Session()
            try:
                for log_data in self._buffer:
                    log_entry = Log(**log_data)
                    session.add(log_entry)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error writing logs to database: {e}")
            finally:
                session.close()
        except Exception as e:
            print(f"Error in database handler: {e}")
        finally:
            self._buffer = []
            self._last_flush = datetime.now()
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Обрабатывает запись лога.
        
        Args:
            record: Запись лога для обработки
        """
        try:
            # Подготавливаем данные для записи
            log_data = {
                "level": record.levelname,
                "logger_name": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Добавляем дополнительные поля, если они есть
            if hasattr(record, "extra"):
                log_data["extra_data"] = json.dumps(record.extra, ensure_ascii=False)
            
            # Добавляем в буфер
            self._buffer.append(log_data)
            
            # Проверяем условия для сброса буфера
            current_time = datetime.now()
            if (len(self._buffer) >= self.batch_size or 
                (current_time - self._last_flush).total_seconds() >= self.batch_timeout):
                # Запускаем асинхронную запись
                asyncio.create_task(self._flush_buffer())
                
        except Exception as e:
            print(f"Error in database handler emit: {e}")

def setup_db_logging() -> None:
    """
    Настраивает логирование в базу данных.
    
    Создает и настраивает:
    - Обработчик для базы данных
    - Уровни логирования
    - Параметры пакетной записи
    """
    try:
        # Создаем обработчик
        db_handler = DatabaseHandler(
            level=logging.INFO,  # Записываем только INFO и выше
            batch_size=100,      # Размер пакета
            batch_timeout=5.0    # Таймаут в секундах
        )
        
        # Добавляем обработчик к корневому логгеру
        root_logger = logging.getLogger()
        root_logger.addHandler(db_handler)
        
        # Логируем информацию о запуске
        logger = logging.getLogger(__name__)
        logger.info("Database logging initialized", extra={
            "batch_size": db_handler.batch_size,
            "batch_timeout": db_handler.batch_timeout
        })
    except Exception as e:
        print(f"Error setting up database logging: {e}")
        raise 