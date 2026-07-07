from fastapi import FastAPI
from sqlalchemy import text

from app.db.base import engine
from app.api.router import api_router

app = FastAPI(title="Price Alerts")

app.include_router(api_router)

@app.get("/health")
async def health():
	async with engine.connect() as conn:
		await conn.execute(text("SELECT 1"))
	return {"status": "ok"}