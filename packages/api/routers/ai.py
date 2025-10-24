from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import schemas, dependencies, ai_service, models

router = APIRouter(prefix="/ai", tags=["AI & Recommendations"])

@router.get("/search/activities", response_model=List[schemas.ActivityPublic])
def search_similar_activities(
    query: str = Query(..., description="Search query for finding similar activities"),
    trip_id: str = Query(None, description="Optional trip ID to filter results"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Search for activities similar to the query using AI-powered semantic search.
    
    Example queries:
    - "outdoor adventure activities"
    - "romantic dinner spots"
    - "cultural museums and exhibits"
    """
    activities = ai_service.find_similar_activities(
        db=db,
        query_text=query,
        trip_id=trip_id,
        limit=limit
    )
    
    if not activities:
        return []
    
    return [schemas.ActivityPublic.model_validate(activity) for activity in activities]

@router.get("/search/recommendations", response_model=List[schemas.RecommendationPublic])
def search_similar_recommendations(
    query: str = Query(..., description="Search query for finding similar destinations"),
    trip_id: str = Query(None, description="Optional trip ID to filter results"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Search for destination recommendations similar to the query using AI.
    
    Example queries:
    - "tropical beach paradise"
    - "historic European cities"
    - "mountain skiing resorts"
    """
    recommendations = ai_service.find_similar_recommendations(
        db=db,
        query_text=query,
        trip_id=trip_id,
        limit=limit
    )
    
    if not recommendations:
        return []
    
    return [schemas.RecommendationPublic.model_validate(rec) for rec in recommendations]

@router.post("/activities/{activity_id}/generate-embedding", status_code=status.HTTP_200_OK)
def generate_activity_embedding(
    activity_id: uuid.UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Generate and store an embedding for an existing activity.
    Useful for retroactively adding AI capabilities to existing data.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    embedding = ai_service.generate_activity_embedding(activity)
    
    if embedding:
        # Use setattr to avoid type checker issues with SQLAlchemy columns
        setattr(activity, 'embedding', embedding)
        db.commit()
        return {"message": "Embedding generated successfully", "dimension": len(embedding)}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured or embedding generation failed"
        )

@router.post("/recommendations/{recommendation_id}/generate-embedding", status_code=status.HTTP_200_OK)
def generate_recommendation_embedding(
    recommendation_id: uuid.UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.UserPublic = Depends(dependencies.get_current_user)
):
    """
    Generate and store an embedding for an existing recommendation.
    """
    recommendation = db.query(models.Recommendation).filter(
        models.Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    embedding = ai_service.generate_recommendation_embedding(recommendation)
    
    if embedding:
        # Use setattr to avoid type checker issues with SQLAlchemy columns
        setattr(recommendation, 'embedding', embedding)
        db.commit()
        return {"message": "Embedding generated successfully", "dimension": len(embedding)}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured or embedding generation failed"
        )
