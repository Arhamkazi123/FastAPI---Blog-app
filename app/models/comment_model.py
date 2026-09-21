from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime, timezone

class CommentBase(SQLModel):
	text: str = Field(min_length=1, max_length=100)

class CommentRead(CommentBase):
	id:int
	user_id: int
	post_id:int
	created_at: datetime

class CommentCreate(CommentBase):
	pass

class Comment(CommentBase,table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	user_id:int=Field(foreign_key="user.id")
	post_id:int=Field(foreign_key="post.id")
	created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc)
  )
