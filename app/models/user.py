from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(100), unique=True)
	hashed_password: Mapped[str] = mapped_column(nullable=False)
	is_active: Mapped[bool] = mapped_column(default=True)
	created_at: Mapped[datetime] = mapped_column(default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())