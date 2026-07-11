from app.clients.webhook import send_webhook
from app.models.alert import Alert


async def send_notification(alert: Alert, price: float) -> None:
	if alert.channel != "webhook":
		raise ValueError(
			f"Unsupported notification channel: {alert.channel}"
		)
	
	payload = {
		"alert_id": alert.id,
		"symbol": alert.symbol,
		"condition": alert.condition,
		"threshold": alert.threshold,
		"price": price,
	}

	await send_webhook(alert.channel_target, payload)
