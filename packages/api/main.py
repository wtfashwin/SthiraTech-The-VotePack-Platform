from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine, Base
Base.metadata.create_all(bind=engine)
import uuid

app = FastAPI(
    title="PackVote API",
    description="Backend for the AI group travel planner."
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Health Check"])
def read_root():
    """Server status check karne ke liye."""
    return {"status": "ok", "message": "Welcome to PackVote API"}

@app.post("/trips/", response_model=schemas.Trip, status_code=status.HTTP_201_CREATED, tags=["Trips"])
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    """Ek naya trip create karta hai."""
    trip_id = str(uuid.uuid4())
    creator_id = "user_placeholder_123"  
    db_trip = models.Trip(id=trip_id, name=trip.name, creatorId=creator_id)
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@app.get("/trips/{trip_id}", response_model=schemas.Trip, tags=["Trips"])
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    """ID se ek specific trip ki details laata hai."""
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@app.post("/trips/{trip_id}/participants/", response_model=schemas.Participant, status_code=status.HTTP_201_CREATED, tags=["Participants"])
def add_participant_to_trip(trip_id: str, participant: schemas.ParticipantCreate, db: Session = Depends(get_db)):
    """Ek trip mein naye participant ko add karta hai."""
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    db_participant = models.Participant(**participant.model_dump(), tripId=trip_id)
    
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

