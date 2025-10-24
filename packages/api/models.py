from sqlalchemy import Column, String, Integer, Enum as SQLAlchemyEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base
from .schemas import TripStatus
from .enums import TripStatus

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(SQLAlchemyEnum(TripStatus), default=TripStatus.GATHERING, nullable=False)
    creatorId = Column(String, nullable=False)
    status = Column(SQLAlchemyEnum(TripStatus), nullable=False, default=TripStatus.PENDING)
    participants = relationship("Participant", back_populates="trip", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="trip", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    tripId = Column(String, ForeignKey("trips.id"))

    trip = relationship("Trip", back_populates="participants")
    survey_response = relationship("SurveyResponse", back_populates="participant", uselist=False, cascade="all, delete-orphan")

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget = Column(Text, nullable=True)
    available_dates = Column(Text, nullable=True)
    vibe = Column(Text, nullable=True)
    dealbreakers = Column(Text, nullable=True)

    participantId = Column(UUID(as_uuid=True), ForeignKey("participants.id"))
    
    participant = relationship("Participant", back_populates="survey_response")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    estimated_cost = Column(Integer, nullable=False)
    justification = Column(Text, nullable=False)
    rank = Column(Integer, nullable=False)

    tripId = Column(String, ForeignKey("trips.id"))

    trip = relationship("Trip", back_populates="recommendations")

