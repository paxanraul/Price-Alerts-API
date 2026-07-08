from datetime import datetime
from sqlalchemy import String, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Alert(Base):
	__tablename__ = "alerts"

	id: Mapped[int] = mapped_column(primary_key=True)
	owner_id: Mapped[int] = mapped_column(ForeignKey="users.id", nullable=False, index=True)
	symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
	condition: Mapped[str] = mapped_column(String(1), nullable=False) # > or <
	threshold: Mapped[float] = mapped_column(nullable=False)
	channel: Mapped[str] = mapped_column(String(20), nullable=False)
	channel_target: Mapped[str] = mapped_column(nullable=False)
	cooldown_seconds: Mapped[int] = mapped_column(default=300)
	state: Mapped[int] = mapped_column(String(20), default="armed")
	is_active: Mapped[bool] = mapped_column(default=True)
	last_triggered_at: Mapped[datetime | None] = mapped_column(nullable=True)
	created_at: Mapped[datetime] = mapped_column(default=func.now())

	__table_args__ = (
		CheckConstraint("condition IN ('>', '<')", name="check_condition"),
		CheckConstraint("state IN ('armed', 'triggered')", name="check_state"),
	)