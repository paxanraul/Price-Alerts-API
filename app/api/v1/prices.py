from fastapi import APIRouter, HTTPException, status
from app.services.price_service import get_price, get_all_prices
from app.workers.poller import SYMBOLS

router = APIRouter("/prices", tags=["prices"])


@router.get("")
async def list_prices():
	return await get_all_prices(SYMBOLS)


@router.get("/{symbol}")
async def get_price_endpoint(symbol: str):
	price = await get_price(symbol.upper())
	if price is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
	return {"symbol": symbol.upper(), "price": price}