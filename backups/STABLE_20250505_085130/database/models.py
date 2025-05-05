"""
Модуль с моделями базы данных.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, conint

class User(BaseModel):
    """
    Модель пользователя.
    """
    id: int = Field(..., description="ID пользователя в Telegram")
    phone_number: str = Field(..., max_length=20, description="Номер телефона пользователя")
    username: Optional[str] = Field(None, max_length=32, description="Username пользователя в Telegram")
    first_name: Optional[str] = Field(None, max_length=64, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=64, description="Фамилия пользователя")
    level: conint(ge=1, le=4) = Field(default=4, description="Уровень пользователя (1-4)")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата регистрации")
    updated_at: datetime = Field(default_factory=datetime.now, description="Дата последнего обновления")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123456789,
                "phone_number": "79991234567",
                "username": "example_user",
                "first_name": "Иван",
                "last_name": "Иванов",
                "level": 4,
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }

class Referral(BaseModel):
    """
    Модель реферальной связи.
    """
    id: int = Field(..., description="ID записи")
    referrer_id: int = Field(..., description="ID пригласившего пользователя")
    referred_id: int = Field(..., description="ID приглашенного пользователя")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания связи")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "referrer_id": 123456789,
                "referred_id": 987654321,
                "created_at": "2024-01-01T12:00:00"
            }
        } 