from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories import user_repo
from app.core.security import hash_password, verify_password
from app.schemas.user import UserCreate


async def register(db: AsyncSession, data: UserCreate) -> User:
	existing = await user_repo.get_by_email(db, data.email)
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такая почта уже зарегистрирована.")
	

	user = User(email=data.email, hashed_password=hash_password(data.password))
	return await user_repo.create(db, user)


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
	user = await user_repo.get_by_email(db, email)
	if not user or not verify_password(password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильная почта или пароль.")
	if not user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователя inactive.")
	
	return user