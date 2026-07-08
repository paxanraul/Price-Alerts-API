from app.clients.exchange import get_prices, ExchangeError
from app.services.price_service import set_prices

SYMBOLS = ["BTC", "ETH"]


async def poll_prices(ctx) -> None:
	try: 
		prices = await get_prices(SYMBOLS)
	except ExchangeError:
		return
	
	await set_prices(prices)