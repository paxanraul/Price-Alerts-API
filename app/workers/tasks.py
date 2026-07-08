from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.poller import poll_prices


async def startup(ctx): 
	pass	


async def shutdown(ctx): 
	pass


class WorkerSettings:
	functions = []
	cron_jobs = []
	on_startup = startup
	on_shutdown = shutdown
	redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)