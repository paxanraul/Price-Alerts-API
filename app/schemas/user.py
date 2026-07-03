from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
	email: EmailStr
	password: str


class UserResponse(BaseModel):
	id: int
	email: EmailStr
	is_active: bool

	model_config = ConfigDict(from_attributes=True)