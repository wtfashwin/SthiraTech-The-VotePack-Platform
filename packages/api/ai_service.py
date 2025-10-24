""" 
AI services for generating embeddings and recommendations using OpenAI.
"""
from typing import List, Optional, Any
import openai
from sqlalchemy.orm import Session
import config
import models
import numpy as np

# Initialize OpenAI client
if config.settings.OPENAI_API_KEY:
    openai.api_key = config.settings.OPENAI_API_KEY

EMBEDDING_MODEL = "text-embedding-3-small"  # 384 dimensions, fast and efficient
EMBEDDING_DIMENSION = 384

def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate an embedding vector for the given text using OpenAI's API.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        A list of floats representing the embedding vector, or None if API key is not set
    """
    if not config.settings.OPENAI_API_KEY:
        print("⚠️  OpenAI API key not set. Skipping embedding generation.")
        return None
    
    try:
        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def generate_activity_embedding(activity: models.Activity) -> Optional[List[float]]:
    """
    Generate an embedding for an activity based on its attributes.
    
    Args:
        activity: The Activity model instance
        
    Returns:
        A list of floats representing the embedding vector
    """
    # Create a rich text representation of the activity
    text_parts: list[str] = [str(activity.title)]
    
    notes = getattr(activity, 'notes', None)
    if notes is not None:
        text_parts.append(str(notes))
    
    location = getattr(activity, 'location', None)
    if location is not None:
        text_parts.append(f"Location: {location}")
    
    combined_text = " | ".join(text_parts)
    return generate_embedding(combined_text)

def generate_recommendation_embedding(recommendation: models.Recommendation) -> Optional[List[float]]:
    """
    Generate an embedding for a recommendation.
    
    Args:
        recommendation: The Recommendation model instance
        
    Returns:
        A list of floats representing the embedding vector
    """
    text_parts: list[str] = [str(recommendation.destination_name)]
    
    description = getattr(recommendation, 'description', None)
    if description is not None:
        text_parts.append(str(description))
    
    justification = getattr(recommendation, 'justification', None)
    if justification is not None:
        text_parts.append(str(justification))
    
    combined_text = " | ".join(text_parts)
    return generate_embedding(combined_text)

def find_similar_activities(
    db: Session,
    query_text: str,
    trip_id: Optional[str] = None,
    limit: int = 5
) -> List[models.Activity]:
    """
    Find activities similar to the query text using vector similarity search.
    
    Args:
        db: Database session
        query_text: The search query
        trip_id: Optional trip ID to filter activities
        limit: Maximum number of results to return
        
    Returns:
        List of similar Activity instances
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query_text)
    
    if not query_embedding:
        return []
    
    # Use pgvector's <-> operator for L2 distance (cosine similarity can use <=>)
    # We'll use a raw SQL query for vector similarity
    from sqlalchemy import text
    
    query = """
        SELECT a.* 
        FROM activities a
        WHERE a.embedding IS NOT NULL
    """
    
    params: dict[str, Any] = {"limit": limit}
    
    if trip_id:
        query += " AND a.trip_id = :trip_id"
        params["trip_id"] = trip_id
    
    query += """
        ORDER BY a.embedding <-> CAST(:embedding AS vector)
        LIMIT :limit
    """
    
    params["embedding"] = query_embedding
    
    result = db.execute(text(query), params)
    activity_ids = [row[0] for row in result.fetchall()]
    
    # Fetch the full Activity objects
    return db.query(models.Activity).filter(models.Activity.id.in_(activity_ids)).all()

def find_similar_recommendations(
    db: Session,
    query_text: str,
    trip_id: Optional[str] = None,
    limit: int = 10
) -> List[models.Recommendation]:
    """
    Find recommendations similar to the query text using vector similarity search.
    
    Args:
        db: Database session
        query_text: The search query (e.g., "beach vacation", "mountain hiking")
        trip_id: Optional trip ID to filter recommendations
        limit: Maximum number of results to return
        
    Returns:
        List of similar Recommendation instances
    """
    query_embedding = generate_embedding(query_text)
    
    if not query_embedding:
        return []
    
    from sqlalchemy import text
    
    query = """
        SELECT r.* 
        FROM recommendations r
        WHERE r.embedding IS NOT NULL
    """
    
    params: dict[str, Any] = {"limit": limit}
    
    if trip_id:
        query += " AND r.trip_id = :trip_id"
        params["trip_id"] = trip_id
    
    query += """
        ORDER BY r.embedding <-> CAST(:embedding AS vector)
        LIMIT :limit
    """
    
    params["embedding"] = query_embedding
    
    result = db.execute(text(query), params)
    rec_ids = [row[0] for row in result.fetchall()]
    
    return db.query(models.Recommendation).filter(models.Recommendation.id.in_(rec_ids)).all()
