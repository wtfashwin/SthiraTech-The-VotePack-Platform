# api/routers/trips.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
import dependencies

router = APIRouter(
    tags=["Trips & Participants"]
)

@router.post("/trips", response_model=schemas.TripPublic, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip: schemas.TripCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Creates a new trip.
    The authenticated user is automatically set as the creator and first participant.
    """
    # Ensure creator details are passed for the first participant
    if not trip.participants:
        trip.participants.append(schemas.ParticipantCreate(
            name=current_user.name or "Anonymous", 
            email=current_user.email
        ))
    
    return crud.create_trip(db=db, trip=trip, creator_id=current_user.id)


@router.get("/{trip_id}", response_model=schemas.TripPublic)
def get_trip(trip_id: uuid.UUID, db: Session = Depends(dependencies.get_db)):
    """
    Gets all details for a specific trip, including participants, itinerary, expenses, etc.
    """
    db_trip = crud.get_trip_by_id(db, trip_id=trip_id)
    if not db_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return db_trip


@router.post("/{trip_id}/participants/", response_model=schemas.ParticipantPublic, status_code=status.HTTP_201_CREATED)
def add_participant_to_trip(
    trip_id: uuid.UUID,
    participant: schemas.ParticipantCreate,
    db: Session = Depends(dependencies.get_db)
):
    """Adds a new participant to an existing trip."""
    db_trip = crud.get_trip_by_id(db, trip_id=trip_id)
    if not db_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    return crud.add_participant_to_trip(db=db, trip_id=trip_id, participant=participant)


@router.post("/{trip_id}/days/", response_model=schemas.ItineraryDayPublic, status_code=status.HTTP_201_CREATED)
def create_itinerary_day(
    trip_id: uuid.UUID,
    day: schemas.ItineraryDayCreate,
    db: Session = Depends(dependencies.get_db)
):
    """Creates a new day in the itinerary for a trip."""
    return crud.create_itinerary_day(db=db, trip_id=trip_id, day=day)


@router.post("/days/{day_id}/activities/", response_model=schemas.ActivityPublic, status_code=status.HTTP_201_CREATED)
def add_activity_to_day(
    day_id: uuid.UUID,
    activity: schemas.ActivityCreate,
    db: Session = Depends(dependencies.get_db)
):
    """Adds a new activity to a specific day in the itinerary."""
    return crud.add_activity_to_day(db=db, day_id=day_id, activity=activity)