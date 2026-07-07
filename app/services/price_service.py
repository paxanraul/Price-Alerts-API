import json
from app.core.redis import redis_client

PRICE_KEY_PREFIX = "price:"


async def set_prices(prices: dict[str, float]) -> None:
	for symbol, price in prices.items():
		await redis_client.set(f"{PRICE_KEY_PREFIX}{symbol}", json.dumps(price))


async def get_price(symbol: str) -> float | None:
	value = await redis_client.get(f"{PRICE_KEY_PREFIX}{symbol}")
	return json.loads(value) if value else None


async def get_all_prices(symbols: list[str]) -> dict[str, float]:
	result = {}
	for symbol in symbols:
		price = await get_price(symbol)
		if price is not None:
			result[symbol] = price
	return result