from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.future import select
import uuid
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from db_connect import get_db
from model.models_note import NoteDB, NoteDisplay, NoteCreate
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, note:NoteCreate):
        try:
            note_id = str(uuid.uuid4())
            db_note = NoteDB(id=note_id, title=note.title, description=note.description)
            self.db.add(db_note)
            await self.db.commit()
            await self.db.refresh(db_note)
            return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all(self, skip: int = 0, limit: int = 10):
        try:
            result = await self.db.execute(select(NoteDB).offset(skip).limit(limit))
            notes = result.scalars().all()
            return [NoteDisplay(id=note.id, created_at=note.created_at, title=note.title, description=note.description) for note in notes]
        except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
    async def update(self, note_id: str, note_data: NoteCreate):  
        try:
            statement = select(NoteDB).where(NoteDB.id == note_id)
            result = await self.db.execute(statement)
            db_note = result.scalars().first()
            if db_note is None:
                raise HTTPException(status_code=404, detail="Note not found")
            db_note.title = note_data.title  
            db_note.description = note_data.description
            await self.db.commit()
            await self.db.refresh(db_note)
            return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete(self, note_id: str):
        try:
            statement = select(NoteDB).where(NoteDB.id == note_id)
            result = await self.db.execute(statement)
            db_note = result.scalars().first()
            if db_note is None:
                raise HTTPException(status_code=404, detail="Note not found")
            await self.db.delete(db_note)
            await self.db.commit()
            return {"message": "Note deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/", response_model=NoteCreate)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    return await note_service.create(note)

@app.get("/notes/", response_model=list[NoteDisplay])
async def get_notes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    return await note_service.get_all(skip, limit)

@app.put("/notes/{note_id}", response_model=NoteCreate)
async def update_note(note_id: str, note_data: NoteCreate, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    return await note_service.update(note_id, note_data)
    
@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    return await note_service.delete(note_id)