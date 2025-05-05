"""
Модуль для настройки и управления логированием.

Этот модуль предоставляет централизованную систему логирования с поддержкой:
- JSON форматирования
- Ротации логов
- Записи в базу данных
- Консольного вывода
- Разных уровней логирования
"""

import os
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys

from .config import settings
from .db_logger import setup_db_logging

# Глобальная переменная для отслеживания инициализации
_logger_initialized = False

# Создаем глобальный объект логгера
logger = logging.getLogger('bot')

class JsonFormatter(logging.Formatter):
    """
    Форматтер для логирования в JSON формате.
    
    Attributes:
        datefmt (str): Формат даты и времени
        encoding (str): Кодировка для вывода
    """
    
    def __init__(self, datefmt: Optional[str] = None, encoding: str = 'utf-8'):
        super().__init__(datefmt=datefmt)
        self.encoding = encoding
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Форматирует запись лога в JSON.
        
        Args:
            record: Запись лога для форматирования
            
        Returns:
            str: JSON строка с данными лога
        """
        try:
            log_data: Dict[str, Any] = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Добавляем дополнительные поля, если они есть
            if hasattr(record, "extra"):
                log_data.update(record.extra)
            
            # Добавляем информацию о процессе
            log_data.update({
                "process_id": os.getpid(),
                "thread_id": record.thread,
                "process_name": record.processName
            })
            
            return json.dumps(log_data, ensure_ascii=False)
        except Exception as e:
            # В случае ошибки возвращаем базовую информацию
            return json.dumps({
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"Error formatting log: {str(e)}",
                "original_message": record.getMessage()
            }, ensure_ascii=False)

def setup_logging() -> None:
    """
    Настраивает систему логирования.
    
    Создает и настраивает:
    - Директорию для логов
    - Обработчики для файлов и консоли
    - Форматтеры
    - Уровни логирования
    - Запись в базу данных
    """
    global _logger_initialized
    
    # Проверка на повторную инициализацию
    if _logger_initialized:
        return
        
    _logger_initialized = True
    
    try:
        # Создаем директорию для логов, если её нет
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Настройка основного логгера
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Форматтер для JSON логов
        json_formatter = JsonFormatter()
        
        # Обработчик для файла с ротацией
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Добавляем обработчики
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Настройка логгеров для внешних библиотек
        logging.getLogger("aiogram").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        
        # Настраиваем логирование в базу данных
        setup_db_logging()
        
        # Логируем информацию о запуске
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized", extra={
            "log_level": settings.LOG_LEVEL,
            "log_file": str(log_dir / settings.LOG_FILE),
            "process_id": os.getpid(),
            "python_version": os.sys.version
        })
    except Exception as e:
        # В случае ошибки выводим в консоль
        print(f"Error setting up logging: {e}")
        raise

# Инициализация логирования при импорте модуля
setup_logging() 