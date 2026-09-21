from sqlmodel import SQLModel,Field
from typing import Optional

class UserBase(SQLModel):
	username:str=Field(unique=True, index=True, min_length=3, max_length=50)
	role:str=Field(default="user")

class UserRead(UserBase):
  id: int

class UserCreate(SQLModel):
  username: str = Field(min_length=3, max_length=50)
  password: str = Field(min_length=6, max_length=100)

class User(UserBase,table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	hashed_password: str
