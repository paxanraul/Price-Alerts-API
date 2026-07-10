import httpx


class WebhookError(Exception):
	pass


async def send_webhook(url: str, payload: dict) -> None:
	try:
		async with httpx.AsyncClient(timeout=5.0) as client:
			response = await client.post(url, json=payload)
			response.raise_for_status()
	except (httpx.TimeoutException, httpx.HTTPStatusError) as error:
		raise WebhookError(str(error)) from error