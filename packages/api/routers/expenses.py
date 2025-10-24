# api/routers/expenses.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas, dependencies

router = APIRouter(
    prefix="/trips/{trip_id}/expenses",
    tags=["Expenses"]
)

@router.post("/", response_model=schemas.ExpensePublic, status_code=status.HTTP_201_CREATED)
def add_expense_to_trip(
    trip_id: uuid.UUID,
    expense: schemas.ExpenseCreate,
    db: Session = Depends(dependencies.get_db)
    # current_user: dict = Depends(dependencies.get_current_user) # You can use this to validate permissions
):
    """
    Adds a new expense to a trip.
    The request body must contain the full expense details, including how it's split.
    The schema automatically validates that the split amounts equal the total.
    """
    # Validation: Ensure the trip exists
    db_trip = crud.get_trip_by_id(db, trip_id=trip_id)
    if not db_trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        
    # Advanced Validation: Ensure all participants in the expense exist in the trip
    participant_ids_in_trip = {p.id for p in db_trip.participants}
    all_expense_participant_ids = {split.participant_id for split in expense.splits}
    all_expense_participant_ids.add(expense.paid_by_id)
    
    if not all_expense_participant_ids.issubset(participant_ids_in_trip):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more participants in the expense do not belong to this trip."
        )

    return crud.create_expense_for_trip(db=db, trip_id=trip_id, expense=expense)


@router.get("/balance/", response_model=List[schemas.Balance])
def get_trip_balance(
    trip_id: uuid.UUID,
    db: Session = Depends(dependencies.get_db)
):
    """
    Calculates and returns the net financial balance for each participant in a trip.
    A positive balance means they are owed money; a negative balance means they owe money.
    """
    return crud.get_balances_for_trip(db=db, trip_id=trip_id)