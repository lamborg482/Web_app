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
from model.models_note import NoteDB
from model.models_display import NoteDisplay
from model.models_create import NoteCreate
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/notes/", response_model=NoteCreate)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    note_id = str(uuid.uuid4())
    db_note = NoteDB(id=note_id, title=note.title, description=note.description)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description)

    

@app.get("/notes/", response_model=list[NoteDisplay])
async def getnotes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NoteDB).offset(skip).limit(limit))
    notes = result.scalars().all()
    return [NoteDisplay(id=note.id, created_at=note.created_at, title=note.title, description=note.description) for note in notes]


@app.put("/notes/{note_id}", response_model=NoteCreate)
async def update_note(note_id: str, note: NoteCreate, db: Session = Depends(get_db)):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.description = note.description
    db.commit()
    return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description)
    
    
    
@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, db: Session = Depends(get_db)):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return JSONResponse(content={"message": "Note deleted successfully"}, status_code=204)