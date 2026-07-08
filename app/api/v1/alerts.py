from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(
	data: AlertCreate,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)
):
	return await alert_service.create_alert(db, data, current_user.id)


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
	limit: int = Query(default=20, le=100),
	offset: int = Query(default=0, ge=0),
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)
):
	return await alert_service.list_alerts(db, current_user.id, limit, offset)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
	alert_id: int,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)
):
	return await alert_service.get_alert(db, alert_id, current_user.id)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
	alert_id: int,
	data: AlertUpdate,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
):
	return await alert_service.update_alert(db, alert_id, data, current_user.id)


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
	alert_id: int,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db)
):
	await alert_service.delete_alert(db, alert_id, current_user.id)