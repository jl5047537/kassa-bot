from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.core.telegram import validate_telegram_data
from app.crud import user as user_crud
from app.db.base import get_db
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/me", response_model=User)
async def create_or_get_user(
    init_data: str,
    db: Session = Depends(get_db)
):
    # Валидация данных от Telegram
    validated_data = validate_telegram_data(init_data)
    if not validated_data or 'user' not in validated_data:
        raise HTTPException(status_code=400, detail="Invalid Telegram data")
    
    user_data = validated_data['user']
    
    # Проверяем существование пользователя
    db_user = user_crud.get_user_by_telegram_id(db, str(user_data['id']))
    if not db_user:
        # Создаем нового пользователя
        user_create = UserCreate(
            telegram_id=str(user_data['id']),
            username=user_data.get('username'),
            avatar=user_data.get('photo_url'),
            user_link=user_data.get('username')
        )
        db_user = user_crud.create_user(db, user_create)
    
    # Создаем JWT токен
    access_token = create_access_token(data={"sub": db_user.id})
    
    return {
        **db_user.__dict__,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    from app.core.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_crud.get_user(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user 