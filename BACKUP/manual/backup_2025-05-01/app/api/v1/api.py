from fastapi import APIRouter
from app.api.v1.endpoints import auth, referral

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(referral.router, prefix="/referral", tags=["referral"]) 