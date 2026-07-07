from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, LoginResponse
from app.services import user_service
from app.core.security import create_access_token
from app.core.redis import redis_client
from app.core.config import settings
from app.api.deps import get_current_user, oauth2_scheme
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
	return await user_service.register(db, data)


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
	user = await user_service.authenticate(db, data.email, data.password)
	token = create_access_token({"sub": str(user.id)})
	return LoginResponse(access_token=token)


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
	ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
	await redis_client.set(f"blacklist:{token}", "1", ex=ttl)
	return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
	return current_user