from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class ReferralCircle(Base):
    __tablename__ = "referral_circles"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.id"), unique=True)
    status = Column(String, default="active")  # active | closed
    referrals_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    owner = relationship("User", back_populates="referral_circle")
    referrals = relationship("Referral", back_populates="circle")
    referral_history = relationship("ReferralHistory", back_populates="circle")

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, index=True)
    circle_id = Column(String, ForeignKey("referral_circles.id"), nullable=False)
    referral_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношения
    circle = relationship("ReferralCircle", back_populates="referrals")
    referral = relationship("User", back_populates="referrals")

class ReferralHistory(Base):
    __tablename__ = "referral_history"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    circle_id = Column(String, ForeignKey("referral_circles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношения
    user = relationship("User", back_populates="referral_history")
    circle = relationship("ReferralCircle", back_populates="referral_history") 