from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from minio import Minio
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from db_connect import get_db
from model.models_note import NoteDB, NoteDisplay, NoteCreate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

minio_client = Minio(
    "minio:9000",
    access_key="minio",
    secret_key="minio123",
    secure=False
)

class NoteService:
    def __init__(self, db: AsyncSession, minio_client: Minio):
        self.db = db
        self.minio_client = minio_client
        self.bucket_name = "images"
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)

    async def upload_image(self, file: UploadFile):
        file_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        self.minio_client.put_object(
            self.bucket_name,
            file_name,
            file.file,
            length=-1,
            part_size=10*1024*1024
        )
        image_url = f"http://localhost:9000/uploads/{self.bucket_name}/{file_name}"
        return image_url

    async def create(self, note: NoteCreate, image_urls: List[str] = None):
        try:
            note_id = str(uuid.uuid4())
            db_note = NoteDB(id=note_id, title=note.title, description=note.description, image_urls=image_urls)
            self.db.add(db_note)
            await self.db.commit()
            await self.db.refresh(db_note)
            return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description, image_urls=db_note.image_urls)
        except Exception as e:
            print(f"Error creating note: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all(self, skip: int = 0, limit: int = 10):
        try:
            result = await self.db.execute(select(NoteDB).offset(skip).limit(limit))
            notes = result.scalars().all()
            return [NoteDisplay(id=note.id, created_at=note.created_at, title=note.title, description=note.description, image_urls=note.image_urls) for note in notes]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def update(self, note_id: str, note_data: NoteCreate):
        try:
            statement = select(NoteDB).where(NoteDB.id == note_id)
            result = await self.db.execute(statement)
            db_note = result.scalars().first()
            if db_note is None:
                raise HTTPException(status_code=404, detail="Note not found")
            if note_data.title is not None:
                db_note.title = note_data.title
            if note_data.description is not None:
                db_note.description = note_data.description
            if note_data.image_urls is not None:
                db_note.image_urls = note_data.image_urls
            else:
                db_note.image_urls = []
            await self.db.commit()
            await self.db.refresh(db_note)
            return NoteDisplay(id=db_note.id, created_at=db_note.created_at, title=db_note.title, description=db_note.description, image_urls=db_note.image_urls)
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

@app.post("/upload-image/", response_model=dict)
async def upload_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db, minio_client)
    image_url = await note_service.upload_image(file)
    return {"image_url": image_url}

@app.post("/notes/", response_model=NoteDisplay)
async def create_note(title: str = Form(...), description: str = Form(...), files: List[UploadFile] = File(None), db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db, minio_client)
    image_urls = []
    if files:
        for file in files:
            image_url = await note_service.upload_image(file)
            image_urls.append(image_url)
    note = NoteCreate(title=title, description=description, image_urls=image_urls)
    return await note_service.create(note, image_urls)

@app.get("/notes/", response_model=list[NoteDisplay])
async def get_notes(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db, minio_client)
    return await note_service.get_all(skip, limit)

@app.put("/notes/{note_id}", response_model=NoteDisplay)
async def update_note(note_id: str, title: Optional[str] = Form(None), description: Optional[str] = Form(None), files: List[UploadFile] = File(None), db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db, minio_client)
    image_urls = []
    if files:
        for file in files:
            image_url = await note_service.upload_image(file)
            image_urls.append(image_url)
    note_data = NoteCreate(title=title, description=description, image_urls=image_urls)
    return await note_service.update(note_id, note_data)

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db, minio_client)
    return await note_service.delete(note_id)
