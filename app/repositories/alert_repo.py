from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert


async def create(db: AsyncSession, alert: Alert) -> Alert:
	db.add(alert)
	await db.commit()
	await db.refresh(alert)
	return alert


async def get_by_id(db: AsyncSession, alert_id: int) -> Alert | None:
	result = await db.execute(select(Alert).where(Alert.id == alert_id))
	return result.scalar_one_or_none()


async def list_by_owner(
		db: AsyncSession, owner_id: int, limit: int = 20, offset: int = 0
) -> list[Alert]:
	result = await db.execute(
		select(Alert)
		.where(Alert.owner_id == owner_id)
		.order_by(Alert.created_at.desc())
		.limit(limit)
		.offset(offset)
	)
	return result.scalars().all()


async def delete(db: AsyncSession, alert: Alert) -> None:
	alert.is_active = False
	await db.commit()