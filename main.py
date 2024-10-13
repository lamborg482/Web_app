from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = psycopg2.connect(
            host='localhost',
            dbname='Web_note',
            user='postgres',
            password='1639',
            port=6666
        )
    return conn

class NoteCreate(BaseModel):
    title: str
    description: str

class NoteDisplay(BaseModel):
    id: str
    created_at: str
    title: str
    description: str
    
@app.post("/notes/", response_model=NoteCreate)
def create_note(note: NoteCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    note_id = str(uuid.uuid4())
    create_at = str(datetime.utcnow().strftime('%Y-%m-%d'))
    try:
        cur.execute("INSERT INTO notes (id, created_at, title, description) VALUES (%s, %s, %s, %s)",
                    (note_id, create_at, note.title, note.description))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return note

    
@app.get("/notes/", response_model=List[NoteDisplay])
def get_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, title, description FROM notes ")
    rows = cur.fetchall()
    notes = [NoteDisplay(id=row[0], created_at=row[1] if row[1] is not None else datetime.now(), title=row[2], description=row[3]) for row in rows]
    return notes

@app.put("/notes/{note_id}", response_model=NoteCreate)
def update_note(note_id: str, note: NoteCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET title = %s, description = %s WHERE id = %s",
                (note.title, note.description, note_id))
    conn.commit()
    cur.close()
    conn.close()
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s",
                (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return JSONResponse(content={"message": "Note deleted successfully"},
                        status_code=204)