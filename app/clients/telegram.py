import httpx

from app.core.config import settings

TELEGRAM_URL = (
	f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
)


class TelegramError(Exception):
	pass


async def send_telegram(chat_id: int, text: str) -> None:
	payload = {
		"chat_id": chat_id,
		"text": text
	}

	try:
		async with httpx.AsyncClient(timeout=5.0) as client:
			response = await client.post(TELEGRAM_URL, json=payload)
			response.raise_for_status()
	except (httpx.RequestError, httpx.HTTPStatusError) as error:
		raise TelegramError(str(error)) from error