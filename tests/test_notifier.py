from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.webhook import WebhookError
from app.models.alert import Alert
from app.models.alert_trigger import AlertTrigger
from app.models.user import User
from app.services import notifier


async def create_alert_and_trigger(
	db: AsyncSession,
	channel: str = "webhook",
) -> tuple[Alert, AlertTrigger]:
	user = User(
		email="owner@example.com",
		hashed_password="hashed-password",
	)
	db.add(user)
	await db.flush()

	alert = Alert(
		owner_id=user.id,
		symbol="BTC",
		condition=">",
		threshold=100.0,
		channel=channel,
		channel_target="http://example.com",
		cooldown_seconds=300,
		state="triggered",
		is_active=True,
	)
	db.add(alert)
	await db.flush()

	trigger = AlertTrigger(
		alert_id=alert.id,
		price_at_trigger=101.0,
	)
	db.add(trigger)
	await db.commit()

	return alert, trigger


async def test_send_notification_marks_delivery_as_sent(
		db_session: AsyncSession,
		monkeypatch,
):
	send_requests = []

	async def fake_send_webhook(url: str, payload: dict) -> None:
		send_requests.append(
			{
				"url": url,
				"payload": payload,
			}
		)

	monkeypatch.setattr(
		notifier,
		"send_webhook",
		fake_send_webhook,
	)

	alert, trigger = await create_alert_and_trigger(db_session)

	delivery = await notifier.send_notification(
		alert,
		db_session,
		trigger,
	)

	assert delivery.status == "sent"
	assert delivery.attempts == 1
	assert delivery.last_error is None
	assert len(send_requests) == 1
	assert send_requests[0]["url"] == alert.channel_target
	assert send_requests[0]["payload"]["price"] == trigger.price_at_trigger


async def test_send_notification_marks_delivery_as_failed_after_retries(
	db_session: AsyncSession,
	monkeypatch,

):
	async def failing_send_webhook(url: str, payload: dict) -> None:
		raise WebhookError("Webhook unavailable")

	async def skip_sleep(seconds: int) -> None:
		return None

	monkeypatch.setattr(
		notifier,
		"send_webhook",
		failing_send_webhook,
	)
	monkeypatch.setattr(
		notifier.asyncio,
		"sleep",
		skip_sleep,
	)

	alert, trigger = await create_alert_and_trigger(db_session)

	delivery = await notifier.send_notification(
		alert,
		db_session,
		trigger,
	)

	assert delivery.status == "failed"
	assert delivery.attempts == notifier.MAX_ATTEMPTS
	assert delivery.last_error == "Webhook unavailable"


async def test_send_notification_fails_for_unsupported_channel(
	db_session: AsyncSession,
):
	alert, trigger = await create_alert_and_trigger(
		db_session,
		channel="email",
	)

	delivery = await notifier.send_notification(alert, db_session, trigger)

	assert delivery.status == "failed"
	assert delivery.attempts == 1
	assert delivery.last_error == "Unsupported notification channel: email"
