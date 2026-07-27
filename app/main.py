from fastapi import FastAPI
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator

from app.db.base import engine
from app.api.router import api_router
from app.api.ws.prices import router as ws_router

app = FastAPI(title="Price Alerts")

Instrumentator().instrument(app).expose(app)

app.include_router(api_router)
app.include_router(ws_router)

@app.get("/health")
async def health():
	async with engine.connect() as conn:
		await conn.execute(text("SELECT 1"))
	return {"status": "ok"}