"""
AI Consensus Engine for PackVote 3.0
Generates and scores itinerary proposals based on group preferences.
"""
from typing import List, Optional, Dict, Any, cast
from decimal import Decimal
from sqlalchemy.orm import Session
import uuid
import logging

import models
import schemas
import config
import google.generativeai as genai

logger = logging.getLogger(__name__)

if config.settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.settings.GEMINI_API_KEY)  # type: ignore[attr-defined]
        logger.info("✅ Gemini API configured for AI consensus")
    except Exception as e:
        logger.error(f"❌ Failed to configure Gemini API: {e}")


def calculate_compatibility_score(
    proposal: Dict[str, Any],
    survey_responses: List[models.SurveyResponse]
) -> float:
    if not survey_responses:
        return 50.0  
    
    total_score = 0.0
    weight_count = 0
    
    # Budget compatibility (40% weight)
    proposal_budget = proposal.get('estimated_budget', 0)
    if proposal_budget > 0:
        budget_scores = []
        for response in survey_responses:
            response_budget = cast(Optional[Decimal], response.budget)
            if response_budget is not None and response_budget > 0:
                # Calculate how close the proposal is to each person's budget
                budget_diff = abs(float(response_budget) - proposal_budget)
                max_budget = max(float(response_budget), proposal_budget)
                budget_match = 1 - (budget_diff / max_budget) if max_budget > 0 else 1
                budget_scores.append(budget_match * 100)
        
        if budget_scores:
            total_score += sum(budget_scores) / len(budget_scores) * 0.4
            weight_count += 0.4
    
    # Vibe/Interest compatibility (40% weight)
    proposal_vibe = proposal.get('vibe', '').lower()
    if proposal_vibe:
        vibe_scores = []
        for response in survey_responses:
            response_vibe = cast(Optional[str], response.vibe)
            if response_vibe:
                # Simple keyword matching for V1
                response_vibe_lower = str(response_vibe).lower()
                common_keywords = set(proposal_vibe.split()) & set(response_vibe_lower.split())
                vibe_match = len(common_keywords) / max(len(proposal_vibe.split()), 1)
                vibe_scores.append(vibe_match * 100)
        
        if vibe_scores:
            total_score += sum(vibe_scores) / len(vibe_scores) * 0.4
            weight_count += 0.4
    
    # Pace compatibility (20% weight)
    proposal_pace = proposal.get('pace', 'moderate').lower()
    pace_mapping = {'relaxed': 1, 'moderate': 2, 'packed': 3}
    proposal_pace_value = pace_mapping.get(proposal_pace, 2)
    
    # Infer pace preference from vibe keywords
    pace_scores = []
    for response in survey_responses:
        response_vibe = cast(Optional[str], response.vibe)
        if response_vibe:
            vibe_lower = str(response_vibe).lower()
            if 'relax' in vibe_lower or 'chill' in vibe_lower:
                preferred_pace = 1
            elif 'adventure' in vibe_lower or 'active' in vibe_lower or 'packed' in vibe_lower:
                preferred_pace = 3
            else:
                preferred_pace = 2
            
            pace_diff = abs(preferred_pace - proposal_pace_value)
            pace_match = 1 - (pace_diff / 2)  # Max diff is 2
            pace_scores.append(pace_match * 100)
    
    if pace_scores:
        total_score += sum(pace_scores) / len(pace_scores) * 0.2
        weight_count += 0.2
    
    # Normalize score
    final_score = total_score / weight_count if weight_count > 0 else 50.0
    return min(max(final_score, 0.0), 100.0)


def generate_proposal_variations(
    trip: models.Trip,
    survey_responses: List[models.SurveyResponse]
) -> List[Dict[str, Any]]:
    """
    Generate 2-3 distinct itinerary proposal variations based on destination and preferences.
    
    Args:
        trip: The Trip model instance
        survey_responses: List of participant survey responses
        
    Returns:
        List of proposal dictionaries
    """
    proposals = []
    
    # Calculate average budget from responses
    budgets = [
        float(cast(Decimal, r.budget)) 
        for r in survey_responses 
        if cast(Optional[Decimal], r.budget) is not None and cast(Decimal, r.budget) > 0
    ]
    avg_budget = sum(budgets) / len(budgets) if budgets else 1000.0
    
    # Collect all vibes/interests
    all_vibes = []
    for response in survey_responses:
        response_vibe = cast(Optional[str], response.vibe)
        if response_vibe:
            all_vibes.append(str(response_vibe))
    combined_vibes = " ".join(all_vibes)
    
    destination = trip.final_destination or "an exciting location"
    
    # Proposal 1: Budget-focused, relaxed pace
    proposals.append({
        'title': f'Budget-Friendly {destination} Adventure',
        'description': f'A cost-effective trip to {destination} focusing on free activities, local experiences, and budget accommodations.',
        'estimated_budget': avg_budget * 0.7,
        'pace': 'relaxed',
        'vibe': 'budget affordable local authentic',
        'activities': [
            'Free walking tours and local markets',
            'Affordable local restaurants',
            'Self-guided exploration',
            'Budget-friendly accommodations'
        ]
    })
    
    # Proposal 2: Balanced/Moderate
    proposals.append({
        'title': f'Balanced {destination} Experience',
        'description': f'A well-rounded trip to {destination} balancing popular attractions with authentic experiences.',
        'estimated_budget': avg_budget,
        'pace': 'moderate',
        'vibe': combined_vibes or 'adventure culture exploration',
        'activities': [
            'Top-rated attractions and landmarks',
            'Mix of guided tours and free time',
            'Variety of dining experiences',
            'Comfortable mid-range accommodations'
        ]
    })
    
    # Proposal 3: Premium/Activity-packed (only if budget allows)
    if avg_budget >= 1500:
        proposals.append({
            'title': f'Premium {destination} Getaway',
            'description': f'An upscale, activity-packed journey through {destination} with curated experiences and premium services.',
            'estimated_budget': avg_budget * 1.3,
            'pace': 'packed',
            'vibe': 'luxury adventure premium exclusive',
            'activities': [
                'Private guided tours',
                'Fine dining experiences',
                'Exclusive activities and events',
                'Premium accommodations with amenities'
            ]
        })
    
    return proposals


def generate_consensus_proposals(
    db: Session,
    trip_id: uuid.UUID
) -> schemas.ConsensusProposalsResponse:
    """
    Main function to generate and score consensus proposals for a trip.
    
    Args:
        db: Database session
        trip_id: UUID of the trip
        
    Returns:
        ConsensusProposalsResponse with scored proposals
    """
    # Fetch trip with participants
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Trip not found")
    
    # Fetch survey responses for all participants
    survey_responses = []
    for participant in trip.participants:
        if participant.survey_response:
            survey_responses.append(participant.survey_response)
    
    # Generate proposal variations
    proposal_dicts = generate_proposal_variations(trip, survey_responses)
    
    # Calculate scores for each proposal
    scored_proposals = []
    for proposal_dict in proposal_dicts:
        score = calculate_compatibility_score(proposal_dict, survey_responses)
        
        scored_proposals.append(schemas.ConsensusProposal(
            title=proposal_dict['title'],
            description=proposal_dict['description'],
            score=score,
            justification=f"This proposal scores {score:.1f}/100 based on group budget preferences, activity interests, and preferred pace.",
            estimated_budget=Decimal(str(proposal_dict['estimated_budget'])).quantize(Decimal('0.01')),
            pace=proposal_dict['pace'],
            activities=proposal_dict['activities']
        ))
    
    # Sort by score (highest first)
    scored_proposals.sort(key=lambda p: p.score, reverse=True)
    
    # Calculate average budget from responses
    budgets = [
        float(cast(Decimal, r.budget)) 
        for r in survey_responses 
        if cast(Optional[Decimal], r.budget) is not None and cast(Decimal, r.budget) > 0
    ]
    avg_budget = Decimal(str(sum(budgets) / len(budgets))).quantize(Decimal('0.01')) if budgets else None
    
    return schemas.ConsensusProposalsResponse(
        proposals=scored_proposals[:3],  # Return top 3
        group_size=len(trip.participants),
        average_budget=avg_budget
    )


def enhance_with_ai_suggestions(
    proposal: Dict[str, Any],
    destination: str
) -> Dict[str, Any]:
    """
    Optional: Use Gemini AI to enhance proposal with specific activity suggestions.
    This is a V2 feature placeholder for future enhancement.
    
    Args:
        proposal: Base proposal dictionary
        destination: Destination name
        
    Returns:
        Enhanced proposal with AI-generated activities
    """
    if not config.settings.GEMINI_API_KEY:
        return proposal
    
    try:
        # Use Gemini to generate specific activity suggestions
        model = genai.GenerativeModel('gemini-pro')  # type: ignore[attr-defined]
        budget_str = f"{proposal['estimated_budget']:.0f}"
        prompt = f"""
        Generate 4-5 specific activity suggestions for a {proposal['pace']} paced trip to {destination} 
        with a budget around {budget_str} USD per person.
        Focus on: {proposal['vibe']}
        
        Return only a simple list of activities, one per line.
        """
        
        response = model.generate_content(prompt)  # type: ignore[attr-defined]
        if response and response.text:
            activities = [line.strip('- ').strip() for line in response.text.split('\n') if line.strip()]
            proposal['activities'] = activities[:5]
    
    except Exception as e:
        logger.error(f"⚠️ AI enhancement failed: {e}")
    
    return proposal
