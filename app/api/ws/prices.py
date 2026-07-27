from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import redis_client
from app.services.price_service import PRICE_CHANNEL


router = APIRouter()


@router.websocket("/ws/prices")
async def stream_prices(websocket: WebSocket) -> None:
	await websocket.accept()

	pubsub = redis_client.pubsub()
	await pubsub.subscribe(PRICE_CHANNEL)

	try:
		async for message in pubsub.listen():
			if message["type"] == "message":
				await websocket.send_text(message["data"])

	except WebSocketDisconnect:
		pass

	finally:
		await pubsub.unsubscribe(PRICE_CHANNEL)
		await pubsub.aclose()
