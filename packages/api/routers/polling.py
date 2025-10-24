# api/routers/polling.py

"""
API Router for managing Polls and Votes within a trip.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # Import for catching DB errors

import crud
import schemas
import dependencies

router = APIRouter(
    tags=["Polling"]
)

# ARCHITECTURE FIX: Polls are linked to a Trip, not an Activity, for more flexibility.
@router.post("/trips/{trip_id}/polls/", response_model=schemas.PollPublic, status_code=status.HTTP_201_CREATED)
def create_poll_for_trip(
    trip_id: uuid.UUID,
    poll_data: schemas.PollCreate, # Input uses the ...Create schema
    db: Session = Depends(dependencies.get_db)
):
    """
    Creates a new poll for a trip with a question and a list of options.
    """
    db_trip = crud.get_trip_by_id(db, trip_id=trip_id)
    if not db_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    # FIX: The argument name in the CRUD function is 'poll'.
    return crud.create_poll_for_trip(db=db, trip_id=trip_id, poll=poll_data)


# SECURITY FIX: Path is more specific and doesn't take insecure data in the body.
@router.post("/polls/options/{option_id}/vote", response_model=schemas.VotePublic, status_code=status.HTTP_201_CREATED)
def cast_vote_on_option(
    option_id: uuid.UUID,
    vote_data: schemas.VoteCreate,  # Contains participant_id
    db: Session = Depends(dependencies.get_db)
):
    """
    Casts a vote for a participant on a specific poll option.
    Prevents a user from voting twice on the same poll.
    """
    try:
        return crud.cast_vote_on_poll(db=db, option_id=option_id, participant_id=vote_data.participant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )