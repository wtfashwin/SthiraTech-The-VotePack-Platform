"""
This file defines the final Pydantic schemas for the PackVote API,
perfectly aligned with the refactored, enterprise-grade models.py.
"""
import uuid
from decimal import Decimal
from datetime import datetime, date, time
from typing import List, Optional
from enum import Enum as PyEnum
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

# --- Enums & Shared Types ---

class TripStatus(str, PyEnum):
    PLANNING = "PLANNING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class UserPublic(BaseModel):
    """Public-facing user information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: EmailStr
    name: Optional[str] = None

# --- Authentication Schemas ---

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=255)  # SHA-256 has no length limit
    name: Optional[str] = Field(None, max_length=100)

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: Optional[uuid.UUID] = None

# --- Base, Create, and Update Schemas ---
# Using a consistent pattern for clear separation of concerns.

class TripBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class TripCreate(TripBase):
    # When creating a trip, we can optionally add the first participants.
    participants: List['ParticipantCreate'] = []

class TripUpdate(TripBase):
    status: Optional[TripStatus] = None
    final_destination: Optional[str] = None

class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class ParticipantCreate(ParticipantBase):
    pass

# THIS WAS THE MISSING PIECE
class ItineraryDayBase(BaseModel):
    date: date
    title: Optional[str] = Field(None, max_length=255)

class ItineraryDayCreate(ItineraryDayBase):
    pass

class ActivityBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    notes: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class PollBase(BaseModel):
    question: str = Field(..., min_length=5, max_length=255)

class PollCreate(PollBase):
    options: List[str] = Field(..., min_length=2)

class VoteCreate(BaseModel):
    participant_id: uuid.UUID

class ExpenseSplitBase(BaseModel):
    participant_id: uuid.UUID
    owed_amount: Decimal = Field(..., gt=0, decimal_places=2)

class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=3, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field("USD", max_length=3)
    date: date
    paid_by_id: uuid.UUID
    activity_id: Optional[uuid.UUID] = None

class ExpenseCreate(ExpenseBase):
    splits: List[ExpenseSplitBase]

    @model_validator(mode='after')
    def check_splits_equal_total(self):
        total_split = sum(split.owed_amount for split in self.splits)
        if total_split != self.amount:
            raise ValueError(f"The sum of splits ({total_split}) must equal the total expense amount ({self.amount}).")
        return self

# --- Public-Facing Response Schemas (for GET requests) ---

class ParticipantPublic(ParticipantBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    trip_id: uuid.UUID

class ExpenseSplitPublic(ExpenseSplitBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    is_settled: bool

class ExpensePublic(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    splits: List[ExpenseSplitPublic] = []

class Balance(BaseModel):
    participant: ParticipantPublic
    net_balance: Decimal

class ActivityPublic(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    expense: Optional[ExpensePublic] = None

class ItineraryDayPublic(ItineraryDayBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    activities: List[ActivityPublic] = []

class VotePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    participant_id: uuid.UUID

class PollOptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    content: str
    votes: List[VotePublic] = []

class PollPublic(PollBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    is_active: bool
    options: List[PollOptionPublic] = []

class RecommendationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    destination_name: str
    description: Optional[str]

class TripPublic(TripBase):
    """The main, top-level response model for a trip."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    creator_id: uuid.UUID  # Changed to UUID to match BaseModel
    status: TripStatus
    final_destination: Optional[str] = None
    participants: List[ParticipantPublic] = []
    recommendations: List[RecommendationPublic] = []
    itinerary_days: List[ItineraryDayPublic] = []
    polls: List[PollPublic] = []
    expenses: List[ExpensePublic] = []

