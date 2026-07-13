from arq.cron import cron
from arq.connections import RedisSettings

from app.core.config import settings
from app.workers.poller import poll_prices
from app.db.base import async_session
from app.models import AlertTrigger
from app.repositories import alert_repo, trigger_repo
from app.services.evaluator import evaluate_alert
from app.services.notifier import send_notification


async def startup(ctx): 
	pass	


async def shutdown(ctx): 
	pass


async def evaluate_alerts_for_symbol(
		ctx,
		symbol: str,
		price: float,
) -> None:
	async with async_session() as db:
		alerts = await alert_repo.get_active_by_symbol(db, symbol)

		for alert in alerts:
			if evaluate_alert(alert, price):
				trigger = AlertTrigger(
					alert_id=alert.id,
					price_at_trigger=price,
				)
				await trigger_repo.create(db, trigger)
				await send_notification(alert, db, trigger)
		
		await db.commit()


class WorkerSettings:
	functions = [evaluate_alerts_for_symbol]
	cron_jobs = [cron(poll_prices, second={0, 15, 30, 45})]
	on_startup = startup
	on_shutdown = shutdown
	redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
