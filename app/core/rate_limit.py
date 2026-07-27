from fastapi import HTTPException, status

from app.core.redis import redis_client


async def check_rate_limit(
		key: str,
		limit: int,
		window_seconds: int,
) -> None:
	count = await redis_client.incr(key)

	if count == 1:
		await redis_client.expire(key, window_seconds)

	if count > limit:
		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail="Too many requests. Try again later.",
		)
	