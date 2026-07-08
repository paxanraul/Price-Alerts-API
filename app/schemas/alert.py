from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class AlertCreate(BaseModel):
	symbol: str = Field(..., min_length=2, max_length=10)
	condition: Literal[">", "<"]
	threshold: float = Field(..., gt=0)
	channel: Literal["webhook", "telegram", "email"]
	channel_target: str
	cooldown_seconds: int = Field(default=300, ge=0)


class AlertUpdate(BaseModel):
	threshold: float | None =	Field(default=None, gt=0)
	is_active: bool | None = None


class AlertResponse(BaseModel):
	id: int
	symbol: str
	condition: str
	threshold: float
	channel: str
	channel_target: str
	cooldown_seconds: int
	state: str
	is_active: bool
	last_triggered_at: datetime | None = None
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)