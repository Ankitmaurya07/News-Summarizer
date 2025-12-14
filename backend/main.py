from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import ml_engine, database

app = FastAPI()

# Allow the Frontend to talk to this Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    url: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/summarize")
def summarize(request: Request, db: Session = Depends(get_db)):
    # Check Cache
    existing = db.query(database.Summary).filter(database.Summary.url == request.url).first()
    if existing:
        return {"summary": existing.summary, "source": "Database (Cache)"}

    # Run AI
    generated_summary = ml_engine.summarize_article(request.url)
    
    # Save to DB
    new_entry = database.Summary(url=request.url, summary=generated_summary)
    db.add(new_entry)
    db.commit()

    return {"summary": generated_summary, "source": "AI Model (Live)"}