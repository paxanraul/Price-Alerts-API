from fastapi import FastAPI, HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from prometheus_fastapi_instrumentator import Instrumentator

from app.db.base import engine
from app.api.router import api_router
from app.api.ws.prices import router as ws_router
from app.core.logging import configure_logging
from app.core.redis import redis_client
from app.clients.exchange import ExchangeError, get_prices

configure_logging()
app = FastAPI(title="Price Alerts")

Instrumentator().instrument(app).expose(app)

app.include_router(api_router)
app.include_router(ws_router)

@app.get("/health")
async def health():
	try:
		async with engine.connect() as conn:
			await conn.execute(text("SELECT 1"))

		await redis_client.ping()
		await get_prices(["BTC"])
	
	except (SQLAlchemyError, RedisError, ExchangeError) as error:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="Dependency unavailable",
		) from error
	
	return {
		"status": "ok",
		"database": "ok",
		"redis": "ok",
		"exchange": "ok",
	}
