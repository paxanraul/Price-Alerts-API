from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery


async def create(db: AsyncSession, delivery: Delivery) -> Delivery:
	db.add(delivery)
	await db.commit()
	await db.refresh(delivery)
	return delivery


async def update(db: AsyncSession, delivery: Delivery) -> Delivery:
	await db.commit()
	await db.refresh(delivery)
	return delivery
