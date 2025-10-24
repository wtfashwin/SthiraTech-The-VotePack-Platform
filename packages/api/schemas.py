from pydantic import BaseModel, EmailStr
from typing import List, Optional
import enum
import uuid
from .enums import TripStatus     
# ===================================================================
# Enums: The Single Source of Truth for Statuses
# ===================================================================

class TripStatus(str, enum.Enum):
    """Defines the possible states a trip can be in."""
    GATHERING = "GATHERING"
    GENERATING = "GENERATING"
    VOTING = "VOTING"
    COMPLETED = "COMPLETED"

# ===================================================================
# Schemas for API Data Shapes
# ===================================================================

# --- Participant ---
class ParticipantBase(BaseModel):
    name: str
    email: EmailStr  # Automatic email validation

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    id: uuid.UUID
    tripId: str

    class ConfigDict:
        from_attributes = True

# --- Survey Response ---
class SurveyResponseBase(BaseModel):
    budget: Optional[str] = None
    available_dates: Optional[str] = None
    vibe: Optional[str] = None
    dealbreakers: Optional[str] = None

class SurveyResponseCreate(SurveyResponseBase):
    pass

class SurveyResponse(SurveyResponseBase):
    id: uuid.UUID
    participantId: uuid.UUID

    class ConfigDict:
        from_attributes = True

# --- Recommendation ---
class RecommendationBase(BaseModel):
    destination_name: str
    description: str
    estimated_cost: int
    justification: str

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id: uuid.UUID
    tripId: str
    rank: int

    class ConfigDict:
        from_attributes = True

# --- Trip (The Core Object) ---
class TripBase(BaseModel):
    name: str

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    id: str
    status: TripStatus
    creatorId: str
    participants: List[Participant] = []
    recommendations: List[Recommendation] = []

    class ConfigDict:
        from_attributes = True

