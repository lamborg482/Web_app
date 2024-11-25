from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from db_connect import Base
from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    description: str