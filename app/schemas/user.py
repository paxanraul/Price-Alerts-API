from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
	email: EmailStr
	password: str


class UserResponse(BaseModel):
	id: int
	email: EmailStr
	is_active: bool
	