from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from db_connect import Base
from pydantic import BaseModel

class NoteDisplay(BaseModel):
    id: str
    created_at: str
    title: str
    description: str