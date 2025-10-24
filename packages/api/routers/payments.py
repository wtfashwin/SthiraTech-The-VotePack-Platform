"""
Payment Router for Stripe Integration (PackVote 3.0)
Handles commitment deposits, Stripe Connect onboarding, and webhooks.
"""
import uuid
from typing import Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session

from .. import config, crud, schemas, models, dependencies

router = APIRouter(prefix="/payments", tags=["Payments"])

# Initialize Stripe only if API key is available
stripe = None
if config.settings.STRIPE_SECRET_KEY:
    try:
        import stripe as stripe_lib  # pyright: ignore[reportMissingImports]
        stripe = stripe_lib
        stripe.api_key = config.settings.STRIPE_SECRET_KEY
    except ImportError:
        print("⚠️ Stripe library not installed")


@router.post("/participants/{participant_id}/stripe-onboarding")
def create_stripe_onboarding_link(
    participant_id: uuid.UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Generate a Stripe Connect onboarding link for a participant to set up payouts.
    
    Args:
        participant_id: UUID of the participant
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Dictionary with onboarding URL
    """
    if not stripe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe integration not configured"
        )
    
    # Get participant
    participant = db.query(models.Participant).filter(
        models.Participant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    try:
        # Create or retrieve Stripe Connect account
        if participant.stripe_account_id:  # pyright: ignore[reportGeneralTypeIssues]
            account_id = participant.stripe_account_id
        else:
            # Create new Connect account
            account = stripe.Account.create(  # type: ignore[attr-defined]
                type="express",
                email=participant.email,
                capabilities={
                    "transfers": {"requested": True},
                },
            )
            account_id = account.id
            
            # Update participant with account ID
            crud.update_participant_stripe_account(db, participant_id, account_id)
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(  # type: ignore[attr-defined]
            account=account_id,
            refresh_url=f"{config.settings.FRONTEND_URL or 'http://localhost:5173'}/trips/{participant.trip_id}",
            return_url=f"{config.settings.FRONTEND_URL or 'http://localhost:5173'}/trips/{participant.trip_id}",
            type="account_onboarding",
        )
        
        return {
            "url": account_link.url,
            "account_id": account_id
        }
    
    except stripe.error.StripeError as e:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/trips/{trip_id}/commit")
def create_commitment_payment(
    trip_id: uuid.UUID,
    deposit_data: schemas.CommitmentDepositCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Create a payment intent for a participant's commitment deposit.
    
    Args:
        trip_id: UUID of the trip
        deposit_data: Commitment deposit details
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Payment intent with client_secret for frontend
    """
    if not stripe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe integration not configured"
        )
    
    # Verify trip exists
    trip = crud.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Verify participant belongs to trip
    participant = db.query(models.Participant).filter(
        models.Participant.id == deposit_data.participant_id,
        models.Participant.trip_id == trip_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in this trip"
        )
    
    try:
        # Create commitment deposit record
        deposit = crud.create_commitment_deposit(
            db=db,
            trip_id=trip_id,
            participant_id=deposit_data.participant_id,
            amount=deposit_data.amount,
            currency=deposit_data.currency
        )
        
        # Create Stripe payment intent
        # Convert amount to cents (Stripe expects smallest currency unit)
        amount_cents = int(deposit_data.amount * 100)
        
        payment_intent = stripe.PaymentIntent.create(  # type: ignore[attr-defined]
            amount=amount_cents,
            currency=deposit_data.currency.lower(),
            metadata={
                "trip_id": str(trip_id),
                "participant_id": str(deposit_data.participant_id),
                "deposit_id": str(deposit.id)
            },
            description=f"Commitment deposit for {trip.name}"
        )
        
        # Update deposit with payment intent ID
        crud.update_deposit_status(
            db=db,
            deposit_id=deposit.id,
            status="pending",
            stripe_payment_intent_id=payment_intent.id
        )
        
        return {
            "client_secret": payment_intent.client_secret,
            "deposit_id": str(deposit.id),
            "amount": deposit_data.amount,
            "currency": deposit_data.currency
        }
    
    except stripe.error.StripeError as e:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(dependencies.get_db)
):
    """
    Handle Stripe webhook events for payment status updates.
    
    Args:
        request: FastAPI request object
        background_tasks: Background task manager
        db: Database session
        
    Returns:
        Success response
    """
    if not stripe or not config.settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhooks not configured"
        )
    
    # Get the webhook payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(  # type: ignore[attr-defined]
            payload, sig_header, config.settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]
        
        # Update deposit status
        deposit = crud.get_deposit_by_payment_intent(db, payment_intent_id)
        if deposit:
            crud.update_deposit_status(db, deposit.id, "paid")
            print(f"✅ Payment succeeded for deposit {deposit.id}")
    
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]
        
        deposit = crud.get_deposit_by_payment_intent(db, payment_intent_id)
        if deposit:
            crud.update_deposit_status(db, deposit.id, "failed")
            print(f"❌ Payment failed for deposit {deposit.id}")
    
    return {"status": "success"}


@router.get("/trips/{trip_id}/deposits")
def get_trip_deposits(
    trip_id: uuid.UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Get all commitment deposits for a trip.
    
    Args:
        trip_id: UUID of the trip
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of deposits
    """
    # Verify trip exists
    trip = crud.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    deposits = db.query(models.CommitmentDeposit).filter(
        models.CommitmentDeposit.trip_id == trip_id
    ).all()
    
    return [schemas.CommitmentDepositPublic.model_validate(d) for d in deposits]
