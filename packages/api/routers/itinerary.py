# api/routers/itinerary.py

"""
API Router for managing Itinerary Days and Activities.
This file keeps all itinerary-related endpoints organized.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, dependencies
from .. import scraping_service

router = APIRouter(
    prefix="/itinerary", # Grouping under a common prefix
    tags=["Itinerary"]
)

@router.post("/trips/{trip_id}/days/", response_model=schemas.ItineraryDayPublic, status_code=status.HTTP_201_CREATED)
def create_new_itinerary_day(
    trip_id: uuid.UUID,
    day_data: schemas.ItineraryDayCreate,
    db: Session = Depends(dependencies.get_db)
    # current_user: dict = Depends(dependencies.get_current_user) # Uncomment for permission checks
):
    """Creates a new day in a trip's itinerary."""
    # Ensure the trip exists before adding a day to it.
    db_trip = crud.get_trip_by_id(db, trip_id)
    if not db_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # FIX: The argument name in the CRUD function is 'day', not 'day_data'.
    return crud.create_itinerary_day(db=db, trip_id=trip_id, day=day_data)


@router.post("/days/{day_id}/activities/", response_model=schemas.ActivityPublic, status_code=status.HTTP_201_CREATED)
def add_new_activity_to_day(
    day_id: uuid.UUID,
    activity_data: schemas.ActivityCreate,
    db: Session = Depends(dependencies.get_db)
    # current_user: dict = Depends(dependencies.get_current_user) # Uncomment for permission checks
):
    """Adds a new activity to a specific itinerary day."""
    # FIX: The argument name in the CRUD function is 'activity', not 'activity_data'.
    return crud.add_activity_to_day(db=db, day_id=day_id, activity=activity_data)


@router.post("/trips/{trip_id}/import-from-url", response_model=schemas.ImportFromUrlResponse)
def import_activities_from_social_url(
    trip_id: uuid.UUID,
    request: schemas.ImportFromUrlRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Import activity suggestions from a social media URL (TikTok, Instagram, YouTube, etc.).
    Uses AI to extract activities from the content.
    """
    # Verify trip exists
    db_trip = crud.get_trip_by_id(db, trip_id)
    if not db_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    try:
        result = scraping_service.import_activities_from_url(request.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import from URL: {str(e)}"
        )