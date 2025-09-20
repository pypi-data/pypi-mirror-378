from datetime import datetime
from pydantic import BaseModel

class LikeBase(BaseModel):
    history_id: int

class LikeCreate(LikeBase):
    pass

class LikeOut(BaseModel):
    id: int
    user_id: int
    history_id: int
    created_at: datetime

    class Config:
        from_attributes = True
