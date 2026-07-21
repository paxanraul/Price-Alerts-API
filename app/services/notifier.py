import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.webhook import WebhookError, send_webhook
from app.clients.telegram import TelegramError, send_telegram
from app.models.alert_trigger import AlertTrigger
from app.models.delivery import Delivery
from app.repositories import delivery_repo
from app.models.alert import Alert

MAX_ATTEMPTS = 3


async def send_notification(alert: Alert, db: AsyncSession, trigger: AlertTrigger) -> Delivery:
	delivery = Delivery(
		trigger_id=trigger.id,
		channel=alert.channel,
		status="pending",
		attempts=0
	)
	await delivery_repo.create(db, delivery)
	
	payload = {
		"alert_id": alert.id,
		"symbol": alert.symbol,
		"condition": alert.condition,
		"threshold": alert.threshold,
		"price": trigger.price_at_trigger,
	}

	telegram_text = (
		f"Alert #{alert.id} triggered!\n"
		f"{alert.symbol} {alert.condition} {alert.threshold}\n"
		f"Current price: {trigger.price_at_trigger}"
	)

	for attempt in range(1, MAX_ATTEMPTS + 1):
		delivery.attempts = attempt

		try:
			if alert.channel != "webhook":
				await send_webhook(alert.channel_target, payload)
			
			elif alert.channel == "telegram":
				await send_telegram(
					alert.channel_target,
					telegram_text,
				)

			else:
				raise ValueError(
					f"Unsupported notification channel: {alert.channel}"
				)
		except (WebhookError, TelegramError) as error:
			delivery.last_error = str(error)

			if attempt == MAX_ATTEMPTS:
				delivery.status = "failed"
				return await delivery_repo.update(db, delivery)
			
			await asyncio.sleep(2 ** (attempt - 1))
		
		except ValueError as error:
			delivery.status = "failed"
			delivery.last_error = str(error)
			return await delivery_repo.update(db, delivery)
		
		else:
			delivery.status = "sent"
			delivery.last_error = None
			return await delivery_repo.update(db, delivery)
	
	return delivery
