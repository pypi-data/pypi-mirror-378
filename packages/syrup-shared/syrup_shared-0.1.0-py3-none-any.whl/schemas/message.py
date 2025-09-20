from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class MessageBase(BaseModel):
    content: str
    chat_id: int

class MessageCreate(MessageBase):
    message_type: str = 'text'
    metadata: dict = {}

class MessageUpdate(BaseModel):
    content: str | None = None

class MessageOut(BaseModel):
    id: int
    content: str
    user_id: int
    chat_id: int
    message_type: str
    metadata: dict | None = {}
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
