from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from db_connect import Base
from pydantic import BaseModel

class NoteDB(Base):
    __tablename__ = 'notes'
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    title = Column(String)
    description = Column(String)
    
class NoteCreate(BaseModel):
    title: str
    description: str
    
class NoteDisplay(BaseModel):
    id: str
    created_at: str
    title: str
    description: str