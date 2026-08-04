import httpx
import pytest

from app.clients import exchange


async def test_get_prices_returns_requested_symbols(monkeypatch):
	class FakeAsyncClient:
		def __init__(self, *args, **kwargs):
			pass

		async def __aenter__(self):
			return self

		async def __aexit__(self, exc_type, exc_value, traceback):
			pass

		async def get(self, url: str):
			return httpx.Response(
				status_code=200,
				json=[
					{"symbol": "BTCUSDT", "price": "62000.50"},
					{"symbol": "ETHUSDT", "price": "3500.25"}
				],
				request=httpx.Request("GET", url)
			)

	monkeypatch.setattr(
		exchange.httpx,
		"AsyncClient",
		FakeAsyncClient,
	)

	prices = await exchange.get_prices(["BTC"])

	assert prices == {"BTC": 62000.50}


async def test_get_prices_raises_exchange_error_on_request_failure(
	monkeypatch,
):
	class FailingAsyncClient:
		def __init__(self, *args, **kwargs):
			pass

		async def __aenter__(self):
			return self

		async def __aexit__(self, exc_type, exc_value, traceback):
			pass

		async def get(self, url: str):
			raise httpx.RequestError(
				"Connection failed",
				request=httpx.Request("GET", url),
			)

	monkeypatch.setattr(
		exchange.httpx,
		"AsyncClient",
		FailingAsyncClient,
	)

	with pytest.raises(
		exchange.ExchangeError,
		match="Failed to fetch prices",
	):
		await exchange.get_prices(["BTC"])
