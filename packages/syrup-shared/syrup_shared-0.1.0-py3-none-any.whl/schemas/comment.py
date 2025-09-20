from datetime import datetime
from typing import List
from pydantic import BaseModel
from schemas.user import UserShortOutWithFollowStatus

class CommentBase(BaseModel):
    content: str
    history_id: int

class CommentCreate(CommentBase):
    comment_type: str = 'text'
    comment_metadata: dict = {}

class CommentUpdate(BaseModel):
    content: str | None

class CommentOut(BaseModel):
    id: int 
    content: str
    created_at: datetime
    updated_at: datetime | None = None
    user_id: int
    history_id: int
    likes: int = 0
    dislikes: int = 0
    comment_type: str = 'text'
    comment_metadata: dict | None = {}

    class Config:
        from_attributes = True
