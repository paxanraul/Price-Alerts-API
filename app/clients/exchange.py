import httpx
import structlog

logger = structlog.get_logger()

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

SYMBOL_TO_PAIR = {
	"BTC": "BTCUSDT",
	"ETH": "ETHUSDT",
}


class ExchangeError(Exception):
	pass


async def get_prices(symbols: list[str]) -> dict[str, float]:
	try:
		async with httpx.AsyncClient(timeout=5.0) as client:
			response = await client.get(BINANCE_URL)
			response.raise_for_status()
	except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
		logger.warning("exchange_unavailable", error=str(e))
		raise ExchangeError("Failed to fetch prices")from e
	
	data = response.json()
	price_by_pair = {item["symbol"]: float(item["price"]) for item in data}

	return {
		symbol: price_by_pair[pair]
		for symbol, pair in SYMBOL_TO_PAIR.items()
		if symbol in symbols and pair in price_by_pair
	}
