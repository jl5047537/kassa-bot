from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    user_link: Optional[str] = None
    referral_id: Optional[str] = None
    level: int = 5
    ton_wallet_address: Optional[str] = None
    wallet_status: bool = False

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None
    user_link: Optional[str] = None
    ton_wallet_address: Optional[str] = None
    wallet_status: Optional[bool] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInDB(User):
    pass 