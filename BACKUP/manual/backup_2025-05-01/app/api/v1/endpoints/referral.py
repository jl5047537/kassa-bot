from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.crud import referral as referral_crud
from app.db.base import get_db
from app.schemas.referral import (
    ReferralCircle,
    ReferralCircleCreate,
    Referral,
    ReferralCreate,
    ReferralHistory
)

router = APIRouter()

@router.post("/circle", response_model=ReferralCircle)
async def create_referral_circle(
    circle: ReferralCircleCreate,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Создаем реферальный круг
    db_circle = referral_crud.create_referral_circle(db, circle)
    return db_circle

@router.get("/circle/{circle_id}", response_model=ReferralCircle)
async def get_referral_circle(
    circle_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Получаем реферальный круг
    circle = referral_crud.get_referral_circle(db, circle_id)
    if not circle:
        raise HTTPException(status_code=404, detail="Referral circle not found")
    
    return circle

@router.post("/referral", response_model=Referral)
async def create_referral(
    referral: ReferralCreate,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Создаем реферал
    db_referral = referral_crud.create_referral(db, referral)
    return db_referral

@router.get("/referrals/{circle_id}", response_model=list[Referral])
async def get_circle_referrals(
    circle_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Получаем рефералов круга
    referrals = referral_crud.get_referrals_by_circle(db, circle_id)
    return referrals

@router.post("/history", response_model=ReferralHistory)
async def create_referral_history(
    history: ReferralHistoryCreate,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Создаем запись в истории
    db_history = referral_crud.create_referral_history(db, history)
    return db_history 