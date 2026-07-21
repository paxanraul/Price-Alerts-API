from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery
from app.models.alert_trigger import AlertTrigger


async def create(db: AsyncSession, delivery: Delivery) -> Delivery:
	db.add(delivery)
	await db.commit()
	await db.refresh(delivery)
	return delivery


async def update(db: AsyncSession, delivery: Delivery) -> Delivery:
	await db.commit()
	await db.refresh(delivery)
	return delivery


async def list_by_alert_id(
		db: AsyncSession,
		alert_id: int
) -> list[Delivery]:
	result = await db.execute(
		select(Delivery)
		.join(
			AlertTrigger,
			Delivery.trigger_id == AlertTrigger.id,
		)
		.where(AlertTrigger.alert_id == alert_id)
		.order_by(Delivery.created_at.desc())
	)
	return result.scalars().all()
