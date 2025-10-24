"""
The final, production-ready CRUD (Create, Read, Update, Delete) service layer.
This module contains all functions that directly interact with the database,
keeping business logic separate from the API routing layer. It is optimized for
both performance (with eager loading) and maintainability.
"""
import uuid
from decimal import Decimal
from collections import defaultdict
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

import models
import schemas
import auth

# --- Trip & Participant CRUD ---

def get_trip_by_id(db: Session, trip_id: uuid.UUID) -> models.Trip | None:
    """
    Retrieves a single trip with all its related data eagerly loaded
    to prevent N+1 query problems. This is the main data retrieval function.
    """
    return db.query(models.Trip).options(
        selectinload(models.Trip.participants),
        selectinload(models.Trip.itinerary_days).selectinload(models.ItineraryDay.activities),
        selectinload(models.Trip.polls).selectinload(models.Poll.options).selectinload(models.PollOption.votes),
        selectinload(models.Trip.expenses).selectinload(models.Expense.splits),
        selectinload(models.Trip.recommendations)
    ).filter(models.Trip.id == trip_id).first()

def create_trip(db: Session, trip: schemas.TripCreate, creator_id: uuid.UUID) -> models.Trip:
    """Creates a new trip and adds any initial participants provided."""
    db_trip = models.Trip(name=trip.name, creator_id=creator_id, start_date=trip.start_date, end_date=trip.end_date)
    
    # Add participants if they are included in the creation request.
    for participant_data in trip.participants:
        # In a real app, you might find an existing user by email first.
        # Here, we create a new participant record linked to the trip.
        db_participant = models.Participant(
            name=participant_data.name,
            email=participant_data.email,
            trip=db_trip
            # user_id would be linked here if finding an existing user
        )
        db.add(db_participant)
        
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def add_participant_to_trip(db: Session, trip_id: uuid.UUID, participant: schemas.ParticipantCreate) -> models.Participant:
    """Adds a new participant, checking for duplicates first."""
    existing_participant = db.query(models.Participant).filter_by(
        trip_id=trip_id, email=participant.email
    ).first()
    if existing_participant:
        # This prevents violating the UniqueConstraint and provides a clear response.
        return existing_participant

    db_participant = models.Participant(trip_id=trip_id, **participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

# --- Itinerary CRUD ---

def create_itinerary_day(db: Session, trip_id: uuid.UUID, day: schemas.ItineraryDayCreate) -> models.ItineraryDay:
    """Creates a new day in the itinerary for a trip."""
    db_day = models.ItineraryDay(trip_id=trip_id, **day.model_dump())
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day

def add_activity_to_day(db: Session, day_id: uuid.UUID, activity: schemas.ActivityCreate) -> models.Activity:
    """Adds a new activity to a specific itinerary day."""
    db_activity = models.Activity(day_id=day_id, **activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

# --- Expense & Balance CRUD ---

def create_expense_for_trip(db: Session, trip_id: uuid.UUID, expense: schemas.ExpenseCreate) -> models.Expense:
    """Creates an expense and its associated splits."""
    db_expense = models.Expense(trip_id=trip_id, **expense.model_dump(exclude={"splits"}))
    db.add(db_expense)
    db.flush() # Use flush to get the expense ID before creating splits

    for split_data in expense.splits:
        db_split = models.ExpenseSplit(
            expense_id=db_expense.id,
            participant_id=split_data.participant_id,
            owed_amount=split_data.owed_amount
        )
        db.add(db_split)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_balances_for_trip(db: Session, trip_id: uuid.UUID) -> list[schemas.Balance]:
    """
    Calculates balances using a simple, readable, and maintainable ORM-based approach.
    This is far more robust than a complex raw SQL query.
    """
    trip = get_trip_by_id(db, trip_id) # Reuse our optimized trip getter
    if not trip or not trip.participants:
        return []

    # Use a defaultdict for cleaner balance tracking
    balances = defaultdict(Decimal)

    # First, calculate what each person is owed from the splits
    for expense in trip.expenses:
        for split in expense.splits:
            balances[split.participant_id] -= split.owed_amount

    # Then, calculate what each person has paid
    for expense in trip.expenses:
        balances[expense.paid_by_id] += expense.amount

    # Create the final response
    participant_map = {p.id: p for p in trip.participants}
    return [
        schemas.Balance(
            participant=participant_map[p_id], 
            net_balance=balance.quantize(Decimal("0.01"))
        ) for p_id, balance in balances.items()
        if p_id in participant_map
    ]

# --- Polling CRUD ---

def create_poll_for_trip(db: Session, trip_id: uuid.UUID, poll: schemas.PollCreate) -> models.Poll:
    """Creates a poll and its options for a trip."""
    # FIX: Correctly handle the list of strings for options
    db_poll = models.Poll(trip_id=trip_id, question=poll.question)
    db.add(db_poll)
    db.flush() # Get the poll ID

    # FIX: Iterate through the list of strings directly
    for option_text in poll.options:
        db_option = models.PollOption(poll_id=db_poll.id, content=option_text)
        db.add(db_option)
    
    db.commit()
    db.refresh(db_poll)
    return db_poll

def cast_vote_on_poll(db: Session, option_id: uuid.UUID, participant_id: uuid.UUID) -> models.Vote:
    """
    Casts a vote for a participant on a poll option.
    Relies on the database's UniqueConstraint to prevent duplicate votes,
    and catches the resulting IntegrityError for a clean API response.
    """
    db_vote = models.Vote(option_id=option_id, participant_id=participant_id)
    db.add(db_vote)
    try:
        db.commit()
        db.refresh(db_vote)
        return db_vote
    except IntegrityError:
        db.rollback()
        raise ValueError("Participant has already voted on this option or poll.")

# --- User Authentication CRUD ---

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Retrieve a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> models.User | None:
    """Retrieve a user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with hashed password."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Hash password (truncation to 72 bytes handled in auth.get_password_hash)
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Password truncation handled in auth.verify_password
    if not auth.verify_password(password, user.hashed_password):  # type: ignore[arg-type]
        return None
    return user

