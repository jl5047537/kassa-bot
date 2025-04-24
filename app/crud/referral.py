from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.referral import ReferralCircle, Referral, ReferralHistory
from app.schemas.referral import ReferralCircleCreate, ReferralCreate, ReferralHistoryCreate

# ReferralCircle CRUD
def get_referral_circle(db: Session, circle_id: str) -> Optional[ReferralCircle]:
    return db.query(ReferralCircle).filter(ReferralCircle.id == circle_id).first()

def get_referral_circle_by_owner(db: Session, owner_id: str) -> Optional[ReferralCircle]:
    return db.query(ReferralCircle).filter(ReferralCircle.owner_id == owner_id).first()

def create_referral_circle(db: Session, circle: ReferralCircleCreate) -> ReferralCircle:
    db_circle = ReferralCircle(**circle.model_dump())
    db.add(db_circle)
    db.commit()
    db.refresh(db_circle)
    return db_circle

def update_referral_circle_status(db: Session, circle_id: str, status: str) -> Optional[ReferralCircle]:
    db_circle = get_referral_circle(db, circle_id)
    if not db_circle:
        return None
    
    db_circle.status = status
    db.commit()
    db.refresh(db_circle)
    return db_circle

# Referral CRUD
def create_referral(db: Session, referral: ReferralCreate) -> Referral:
    db_referral = Referral(**referral.model_dump())
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral

def get_referrals_by_circle(db: Session, circle_id: str) -> List[Referral]:
    return db.query(Referral).filter(Referral.circle_id == circle_id).all()

def update_referral_wallet_status(db: Session, referral_id: str, wallet_connected: bool) -> Optional[Referral]:
    db_referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not db_referral:
        return None
    
    db_referral.wallet_connected = wallet_connected
    db.commit()
    db.refresh(db_referral)
    return db_referral

# ReferralHistory CRUD
def create_referral_history(db: Session, history: ReferralHistoryCreate) -> ReferralHistory:
    db_history = ReferralHistory(**history.model_dump())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_user_referral_history(db: Session, user_id: str) -> List[ReferralHistory]:
    return db.query(ReferralHistory).filter(ReferralHistory.user_id == user_id).all() 