from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.crud import user as user_crud
from app.db.base import get_db
from app.schemas.user import User

router = APIRouter()

@router.post("/connect", response_model=User)
async def connect_wallet(
    wallet_address: str,
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Обновляем данные кошелька
    user = user_crud.update_wallet(db, payload["sub"], wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/status", response_model=User)
async def get_wallet_status(
    token: str,
    db: Session = Depends(get_db)
):
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Получаем данные пользователя
    user = user_crud.get_user(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user 