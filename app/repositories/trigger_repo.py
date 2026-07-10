from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_trigger import AlertTrigger


async def create(db: AsyncSession, trigger: AlertTrigger) -> AlertTrigger:
	db.add(trigger)
	await db.commit()
	await db.refresh(trigger)
	return trigger