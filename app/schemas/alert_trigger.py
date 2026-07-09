from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertTriggerResponse(BaseModel):
	id: int
	alert_id: int
	price_at_trigger: float
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)