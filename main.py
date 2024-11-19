from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
import uuid
from datetime import datetime

app = FastAPI()
DATABASE_URL = "postgresql://postgres:1639@localhost:6666/Web_note"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NoteDB(Base):
    __tablename__ = 'notes'
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
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
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.post("/notes/", response_model=NoteCreate)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    note_id = str(uuid.uuid4())
    db_note = NoteDB(id=note_id, title=note.title, description=note.description)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description)

    
@app.get("/notes/", response_model=list[NoteDisplay])
async def get_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
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