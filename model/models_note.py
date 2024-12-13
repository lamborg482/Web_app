from sqlalchemy import Column, String, DateTime, ARRAY
from sqlalchemy.sql import func
from db_connect import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class NoteDB(Base):
    __tablename__ = 'notes'
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    title = Column(String)
    description = Column(String)
    image_urls = Column(ARRAY(String))

class NoteCreate(BaseModel):
    title: str
    description: str
    image_urls: Optional[List[str]] = None

class NoteDisplay(BaseModel):
    id: str
    created_at: datetime
    title: str
    description: str
    image_urls: Optional[List[str]] = None
