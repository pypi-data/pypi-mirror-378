from datetime import datetime
from pydantic import BaseModel

class FriendBase(BaseModel):
    friend_id: int

class FriendCreate(FriendBase):
    pass

class FriendOut(BaseModel):
    id: int
    user_id: int
    friend_id: int
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
