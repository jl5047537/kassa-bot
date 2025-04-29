from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    user_link = Column(String, nullable=True)
    referral_id = Column(String, ForeignKey("users.id"), nullable=True)
    level = Column(Integer, default=0)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    referred_by = relationship("User", remote_side=[id], backref="referrals")
    referral_circle = relationship("ReferralCircle", back_populates="owner", uselist=False)
    referral_history = relationship("ReferralHistory", back_populates="user")
    referrals = relationship("Referral", back_populates="referral") 