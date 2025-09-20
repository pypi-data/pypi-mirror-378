from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict

class HistoryCreate(BaseModel):
    title: str
    description: str | None = None  

class HistoryOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    likes: int
    dislikes: int
    comments: int
    views: int
    author_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class HistoryOutShort(BaseModel):
    id: int
    title: str
    description: str | None = None
    likes: int
    dislikes: int
    comments: int
    views: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class HistoryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class HistoryFilesUpdate(BaseModel):
    attached_file_ids: List[int]

class HistoryIdsIn(BaseModel):
    ids: List[int]
