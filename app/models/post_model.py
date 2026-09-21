from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime, timezone

class PostBase(SQLModel):
	title: str = Field(min_length=1, max_length=50)
	content: str = Field(min_length=1, max_length=1000)

class PostRead(PostBase):
	id:int
	user_id: int
	created_at: datetime

class PostCreate(PostBase):
	pass

class Post(PostBase,table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	user_id:int=Field(foreign_key="user.id")
	created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc)
  )
