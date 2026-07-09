from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate
from app.repositories import alert_repo


async def create_alert(db: AsyncSession, data: AlertCreate, owner_id: int) -> Alert:
	alert = Alert(**data.model_dump(), owner_id=owner_id)
	return await alert_repo.create(db, alert)


async def list_alerts(db: AsyncSession, owner_id: int, limit: int, offset: int) -> list[Alert]: 
	return await alert_repo.list_by_owner(db, owner_id, limit, offset)


async def get_alert(db: AsyncSession, alert_id: int, owner_id: int) -> Alert:
	alert = await alert_repo.get_by_id(db, alert_id)
	if not alert or alert.owner_id != owner_id:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
	return alert


async def update_alert(db: AsyncSession, alert_id: int, data: AlertUpdate, owner_id: int) -> Alert:
	alert = await get_alert(db, alert_id, owner_id)
	for key, value in data.model_dump(exclude_unset=True).items():
		setattr(alert, key, value)
	return await alert_repo.update(db, alert)
	

async def delete_alert(db: AsyncSession, alert_id: int, owner_id: int) -> None:
	alert = await get_alert(db, alert_id, owner_id)
	await alert_repo.delete(db, alert)