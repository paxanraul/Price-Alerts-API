from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Delivery(Base):
	__tablename__ = "deliveries"

	id: Mapped[int] = mapped_column(primary_key=True)
	trigger_id: Mapped[int] = mapped_column(
		ForeignKey("alert_triggers.id"),
		nullable=False,
		index=True,
	)
	channel: Mapped[str] = mapped_column(String(20), nullable=False)
	status: Mapped[str] = mapped_column(String(20), default="pending")
	attempts: Mapped[int] = mapped_column(default=0)
	last_error: Mapped[str | None] = mapped_column(nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

	__table_args__ = (
		CheckConstraint(
			"status IN ('pending', 'sent', 'failed')",
			name="check_delivery_status",
		),
	)