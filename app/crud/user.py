from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: str) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_wallet(db: Session, user_id: str, wallet_address: str) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.ton_wallet_address = wallet_address
    db_user.wallet_status = True
    
    db.commit()
    db.refresh(db_user)
    return db_user 