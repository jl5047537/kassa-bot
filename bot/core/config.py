"""
Модуль с конфигурацией бота.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Настройки приложения"""
    # Настройки базы данных
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Настройки бота
    TELEGRAM_BOT_TOKEN: str
    USER_CONFIG_FILE: str = "user_config.json"
    
    # Настройки JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки приложения
    PROJECT_NAME: str = "Kassa Bot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/bot.log"
    
    # Настройки администратора
    MAIN_ADMIN_ID: int
    ADMIN_NOTIFICATION_ENABLED: bool = True
    
    # Настройки уровней
    LEVEL_1_REQUIREMENT: int = 100
    LEVEL_2_REQUIREMENT: int = 500
    LEVEL_3_REQUIREMENT: int = 1000
    
    class Config:
        env_file = "config.env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Создаем экземпляр настроек
settings = Settings()

# Создаем директорию для логов, если её нет
os.makedirs("logs", exist_ok=True)

# Формируем URL для базы данных
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}" 