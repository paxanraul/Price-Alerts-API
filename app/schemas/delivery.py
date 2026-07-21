from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeliveryResponse(BaseModel):
	id: int
	trigger_id: int
	channel: str
	status: str
	attempts: int
	last_error: str | None = None
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
