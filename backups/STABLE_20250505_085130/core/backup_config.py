"""
Конфигурация системы бэкапов.
"""

from typing import Dict, Any
from datetime import time

# Конфигурация бэкапов
BACKUP_CONFIG: Dict[str, Any] = {
    # Расписание бэкапов
    "schedule": {
        "enabled": True,  # Включить автоматические бэкапы
        "daily_time": time(3, 0),  # Время ежедневного бэкапа (03:00)
        "keep_last": 7,  # Хранить последние 7 бэкапов
    },
    
    # Уведомления в Telegram
    "notifications": {
        "enabled": True,  # Включить уведомления
        "chat_id": None,  # ID чата для уведомлений
        "include_metrics": True,  # Включать метрики в уведомления
    },
    
    # Настройки восстановления
    "restore": {
        "verify_integrity": True,  # Проверять целостность при восстановлении
        "default_target": "restored",  # Директория по умолчанию для восстановления
    },
    
    # Директории для бэкапа
    "source_dirs": [
        "bot",
        "docs",
        "scripts",
        "tests"
    ],
    
    # Исключения
    "exclude_dirs": [
        "__pycache__",
        ".pytest_cache",
        "venv",
        "node_modules"
    ],
    "exclude_files": [
        ".env",
        ".gitignore",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    ]
} 