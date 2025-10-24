"""
The final, complete database schema for the PackVote Super-App,
now with pgvector support for AI features.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Enum as SQLAlchemyEnum,
    Date,
    Time,
    Integer,
    Numeric,
    Text,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR


class TripStatus(PyEnum):
    PLANNING = "PLANNING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

# --- Base Configuration ---
# A base model that provides common columns like ID and timestamps.
class BaseModel(object):
    """A mixin for common columns like UUID primary key and timestamps."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), onupdate=lambda: int(datetime.utcnow().timestamp()), nullable=False)

Base = declarative_base(cls=BaseModel)

# --- User Model for Authentication ---

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}')>"

# --- Core Trip and Participant Models ---

class Trip(Base):
    __tablename__ = "trips"

    name = Column(String(100), nullable=False, index=True)
    # Creator ID as UUID (assuming integration with auth system that uses UUIDs)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SQLAlchemyEnum(TripStatus), default=TripStatus.PLANNING, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    final_destination = Column(String(255), nullable=True)
    
    # Optional commitment deposit for reducing dropouts
    commitment_amount = Column(Numeric(10, 2), nullable=True)
    commitment_currency = Column(String(3), default="USD", nullable=True)

    # Relationships
    participants = relationship("Participant", back_populates="trip", cascade="all, delete-orphan", lazy="selectin")
    recommendations = relationship("Recommendation", back_populates="trip", cascade="all, delete-orphan")
    itinerary_days = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryDay.date")
    polls = relationship("Poll", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")
    commitment_deposits = relationship("CommitmentDeposit", back_populates="trip", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trip(name='{self.name}', status='{self.status.value}')>"

class Participant(Base):
    __tablename__ = "participants"

    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    
    # Stripe Connect account ID for receiving payouts
    stripe_account_id = Column(String(255), nullable=True)
    
    # Ensures a user can't be added to the same trip twice
    __table_args__ = (UniqueConstraint('email', 'trip_id', name='_email_trip_uc'),)

    # Relationships
    trip = relationship("Trip", back_populates="participants")
    survey_response = relationship("SurveyResponse", back_populates="participant", uselist=False, cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="participant", cascade="all, delete-orphan")
    expenses_paid = relationship("Expense", back_populates="paid_by", foreign_keys="[Expense.paid_by_id]")
    expense_splits = relationship("ExpenseSplit", back_populates="participant", cascade="all, delete-orphan")
    commitment_deposits = relationship("CommitmentDeposit", back_populates="participant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Participant(name='{self.name}', email='{self.email}')>"

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False, unique=True)
    
    # Use Numeric for budget to avoid floating point issues and allow precise queries
    budget = Column(Numeric(10, 2), nullable=True)
    # Use JSONB for flexible, queryable structured data like date ranges
    # Example: [{"start": "2025-12-20", "end": "2025-12-30"}]
    available_dates = Column(JSONB, nullable=True)
    # Text is better for potentially long user inputs
    vibe = Column(Text, nullable=True)
    dealbreakers = Column(Text, nullable=True)

    # Relationships
    participant = relationship("Participant", back_populates="survey_response")

    def __repr__(self):
        return f"<SurveyResponse(participant_id='{self.participant_id}', budget={self.budget})>"

# --- AI-Powered Recommendation and Polling Models ---

class Recommendation(Base):
    """Represents a potential point of interest, city, or activity."""
    __tablename__ = "recommendations"

    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    source = Column(String(50), default="user") # 'user', 'ai_generated', etc.
    destination_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    justification = Column(Text, nullable=True)
    # Use Integer for rank for proper sorting and calculations
    rank = Column(Integer, default=0)
    
    # Vector column for AI similarity search using Google Gemini (768 dimensions)
    # To use this, you need to run `CREATE EXTENSION IF NOT EXISTS vector;` in your PostgreSQL DB.
    embedding: Mapped[Optional[list[float]]] = mapped_column(VECTOR(768), nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(destination_name='{self.destination_name}')>"

class Poll(Base):
    __tablename__ = "polls"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    question = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    allow_multiple_votes = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    trip = relationship("Trip", back_populates="polls")
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Poll(question='{self.question}')>"

class PollOption(Base):
    __tablename__ = "poll_options"
    
    poll_id = Column(UUID(as_uuid=True), ForeignKey("polls.id"), nullable=False)
    content = Column(Text, nullable=False)
    # Optionally link an option directly to a recommendation
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=True)
    
    # Relationships
    poll = relationship("Poll", back_populates="options")
    votes = relationship("Vote", back_populates="option", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PollOption(content='{self.content[:30]}...')>"

class Vote(Base):
    __tablename__ = "votes"
    
    option_id = Column(UUID(as_uuid=True), ForeignKey("poll_options.id"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    
    # A participant can only vote once per poll (if not multiple choice)
    # You would enforce the single-vote logic in your service layer if allow_multiple_votes is false.
    __table_args__ = (UniqueConstraint('option_id', 'participant_id', name='_option_participant_uc'),)

    # Relationships
    option = relationship("PollOption", back_populates="votes")
    participant = relationship("Participant", back_populates="votes")
    
    def __repr__(self):
        return f"<Vote(participant_id='{self.participant_id}', option_id='{self.option_id}')>"

# --- Itinerary and Activity Models ---

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    date = Column(Date, nullable=False)
    title = Column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint('trip_id', 'date', name='_trip_date_uc'),)

    # Relationships
    trip = relationship("Trip", back_populates="itinerary_days")
    activities = relationship("Activity", back_populates="day", cascade="all, delete-orphan", order_by="Activity.start_time")

    def __repr__(self):
        return f"<ItineraryDay(date='{self.date}', title='{self.title}')>"

class Activity(Base):
    __tablename__ = "activities"

    day_id = Column(UUID(as_uuid=True), ForeignKey("itinerary_days.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    location = Column(String(255), nullable=True)
    
    # Vector column for AI similarity search using Google Gemini (768 dimensions)
    embedding: Mapped[Optional[list[float]]] = mapped_column(VECTOR(768), nullable=True)
    
    # Relationships
    day = relationship("ItineraryDay", back_populates="activities")
    expense = relationship("Expense", back_populates="activity", uselist=False)

    def __repr__(self):
        return f"<Activity(title='{self.title}', start_time='{self.start_time}')>"
        
# --- Expense Tracking Models (Splitwise Functionality) ---

class Expense(Base):
    __tablename__ = "expenses"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    paid_by_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=True)

    # Relationships
    trip = relationship("Trip", back_populates="expenses")
    paid_by = relationship("Participant", back_populates="expenses_paid", foreign_keys=[paid_by_id])
    activity = relationship("Activity", back_populates="expense")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Expense(description='{self.description}', amount={self.amount})>"

class ExpenseSplit(Base):
    """Defines how much each participant owes for a specific expense."""
    __tablename__ = "expense_splits"
    
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    owed_amount = Column(Numeric(10, 2), nullable=False)
    is_settled = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    expense = relationship("Expense", back_populates="splits")
    participant = relationship("Participant", back_populates="expense_splits")
    
    def __repr__(self):
        return f"<ExpenseSplit(participant_id='{self.participant_id}', owed={self.owed_amount}, settled={self.is_settled})>"

# --- Commitment & Escrow Models ---

class CommitmentDeposit(Base):
    """Tracks commitment deposits for trip participants using Stripe."""
    __tablename__ = "commitment_deposits"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Stripe payment intent ID for tracking the payment
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True)
    
    # Status: 'pending', 'paid', 'refunded', 'failed'
    status = Column(String(50), default="pending", nullable=False)
    
    # Relationships
    trip = relationship("Trip", back_populates="commitment_deposits")
    participant = relationship("Participant", back_populates="commitment_deposits")
    
    def __repr__(self):
        return f"<CommitmentDeposit(participant_id='{self.participant_id}', amount={self.amount}, status='{self.status}')>"