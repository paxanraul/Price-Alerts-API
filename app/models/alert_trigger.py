from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AlertTrigger(Base):
	__tablename__ = "alert_triggers"

	id: Mapped[int] = mapped_column(primary_key=True)
	alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), nullable=False, index=True)
	price_at_trigger: Mapped[float] = mapped_column(nullable=False)
	created_at: Mapped[datetime] = mapped_column(default=func.now())