import pytest
from fastapi import HTTPException

from app.core.rate_limit import check_rate_limit


async def test_rate_limit_allows_requests_within_limit(fake_redis):
	key = "rate_limit:alerts:1"

	for _ in range(5):
		await check_rate_limit(
			key=key,
			limit=5,
			window_seconds=60,
		)

	assert fake_redis.data[key] == 5 
	assert fake_redis.expirations[key] == 60


async def test_rate_limit_raises_429_after_limit(fake_redis):
	key = "rate_limit:alerts:1"

	for _ in range(5):
		await check_rate_limit(
			key=key,
			limit=5,
			window_seconds=60,
		)

	with pytest.raises(HTTPException) as error:
		await check_rate_limit(
			key=key,
			limit=5,
			window_seconds=60,
		)

	assert error.value.status_code == 429
