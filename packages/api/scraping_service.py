"""
Web Scraping Service for PackVote 3.0
Extracts activity suggestions from social media URLs (TikTok, Instagram, YouTube, etc.)
"""
from typing import List, Optional, Dict, Any
import re
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

from . import config, schemas

# Initialize Gemini if API key is available
if config.settings.GEMINI_API_KEY:
    genai.configure(api_key=config.settings.GEMINI_API_KEY)  # type: ignore[attr-defined]

# Common user agent to avoid blocking
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


def detect_platform(url: str) -> Optional[str]:
    """
    Detect the platform from the URL.
    
    Args:
        url: The URL to analyze
        
    Returns:
        Platform name or None
    """
    url_lower = url.lower()
    
    if 'tiktok.com' in url_lower:
        return 'TikTok'
    elif 'instagram.com' in url_lower:
        return 'Instagram'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'pinterest.com' in url_lower:
        return 'Pinterest'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X'
    
    return 'Unknown'


def extract_text_from_url(url: str) -> Optional[str]:
    """
    Fetch and extract text content from a URL.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Extracted text content or None
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'header', 'footer', 'nav']):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit to first 2000 characters to avoid overwhelming the LLM
        return text[:2000] if text else None
    
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch URL: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error parsing content: {e}")
        return None


def extract_activities_with_ai(
    text_content: str,
    url: str,
    platform: Optional[str] = None
) -> List[schemas.ImportedActivitySuggestion]:
    """
    Use AI (Gemini) to extract structured activity suggestions from text.
    
    Args:
        text_content: Scraped text from the URL
        url: Original URL for reference
        platform: Detected platform name
        
    Returns:
        List of ImportedActivitySuggestion objects
    """
    if not config.settings.GEMINI_API_KEY:
        print("⚠️ Gemini API key not set. Cannot extract activities.")
        return []
    
    try:
        model = genai.GenerativeModel('gemini-pro')  # type: ignore[attr-defined]
        
        prompt = f"""
        Analyze the following text extracted from a {platform or 'social media'} post/page and extract potential travel activities.
        
        Text content:
        {text_content[:1500]}
        
        Extract 1-5 distinct travel activities mentioned. For each activity, provide:
        1. title: A short, clear title (e.g., "Visit Eiffel Tower")
        2. notes: Any relevant details or description
        3. location: Location/address if mentioned
        4. estimated_duration: Approximate time needed (e.g., "2 hours", "half day")
        
        Return ONLY valid JSON array format like this:
        [
          {{
            "title": "Activity Title",
            "notes": "Description or tips",
            "location": "Place name or address",
            "estimated_duration": "Time estimate"
          }}
        ]
        
        If no clear activities are found, return an empty array: []
        IMPORTANT: Return ONLY the JSON array, no other text.
        """
        
        response = model.generate_content(prompt)  # type: ignore[attr-defined]
        
        if not response or not response.text:
            return []
        
        # Try to extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = re.sub(r'^```json?\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
        
        # Parse JSON
        activities_data = json.loads(response_text)
        
        if not isinstance(activities_data, list):
            return []
        
        # Convert to schema objects
        suggestions = []
        for activity in activities_data[:5]:  # Max 5 activities
            if not isinstance(activity, dict) or 'title' not in activity:
                continue
            
            # Calculate confidence based on completeness
            confidence = 0.5
            if activity.get('location'):
                confidence += 0.2
            if activity.get('notes'):
                confidence += 0.2
            if activity.get('estimated_duration'):
                confidence += 0.1
            
            suggestions.append(schemas.ImportedActivitySuggestion(
                title=activity.get('title', 'Untitled Activity')[:255],
                notes=activity.get('notes'),
                location=activity.get('location'),
                estimated_duration=activity.get('estimated_duration'),
                confidence=min(confidence, 1.0)
            ))
        
        return suggestions
    
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse AI response as JSON: {e}")
        return []
    except Exception as e:
        print(f"⚠️ AI extraction failed: {e}")
        return []


def import_activities_from_url(url: str) -> schemas.ImportFromUrlResponse:
    """
    Main function to import activities from a social media URL.
    
    Args:
        url: The URL to import from
        
    Returns:
        ImportFromUrlResponse with suggested activities
    """
    # Detect platform
    platform = detect_platform(url)
    
    # Extract text from URL
    text_content = extract_text_from_url(url)
    
    if not text_content:
        return schemas.ImportFromUrlResponse(
            url=url,
            suggested_activities=[],
            source_platform=platform
        )
    
    # Use AI to extract activities
    suggestions = extract_activities_with_ai(text_content, url, platform)
    
    return schemas.ImportFromUrlResponse(
        url=url,
        suggested_activities=suggestions,
        source_platform=platform
    )


def create_fallback_suggestions(url: str, platform: Optional[str]) -> List[schemas.ImportedActivitySuggestion]:
    """
    Create fallback suggestions when scraping/AI extraction fails.
    
    Args:
        url: Original URL
        platform: Detected platform
        
    Returns:
        List of generic activity suggestions
    """
    return [
        schemas.ImportedActivitySuggestion(
            title=f"Activity from {platform or 'social media'}",
            notes=f"Manually review content from: {url}",
            location=None,
            estimated_duration=None,
            confidence=0.3
        )
    ]
