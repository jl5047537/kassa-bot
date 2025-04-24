from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReferralCircleBase(BaseModel):
    owner_id: str
    status: str = "active"
    referrals_count: int = 0

class ReferralCircleCreate(ReferralCircleBase):
    pass

class ReferralCircle(ReferralCircleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReferralBase(BaseModel):
    circle_id: str
    referral_id: str
    wallet_connected: bool = False

class ReferralCreate(ReferralBase):
    pass

class Referral(ReferralBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReferralHistoryBase(BaseModel):
    user_id: str
    circle_id: str

class ReferralHistoryCreate(ReferralHistoryBase):
    pass

class ReferralHistory(ReferralHistoryBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True 