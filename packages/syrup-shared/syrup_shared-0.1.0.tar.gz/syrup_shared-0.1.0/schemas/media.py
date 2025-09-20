from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class MediaBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    file_key: str

class MediaCreate(MediaBase):
    pass

class MediaOut(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    file_key: str
    url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
