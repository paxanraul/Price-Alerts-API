from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.redis import redis_client
from app.repositories import user_repo
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
		token: str = Depends(oauth2_scheme),
		db: AsyncSession = Depends(get_db),
) -> User:
	is_blacklisted = await redis_client.get(f"blacklist:{token}")
	if is_blacklisted:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен был отозван.")
	
	payload = decode_access_token(token)
	if payload is None:
		raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Недействительный или истекший токен.")
	
	user_id = payload.get("sub")
	user = await user_repo.get_by_id(db, int(user_id))
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")
	if not user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительный аккаунт пользователя.")
	
	return user