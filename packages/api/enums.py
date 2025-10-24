from enum import Enum

class TripStatus(str, Enum):
    GATHERING = "gathering"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
