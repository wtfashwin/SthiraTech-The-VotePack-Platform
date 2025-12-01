"""
Utility functions for security and data sanitization.
"""
import bleach
from typing import Optional

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(text: Optional[str]) -> Optional[str]:
    """
    Sanitize HTML input to prevent XSS attacks.
    Allows only safe HTML tags and attributes.
    """
    if not text:
        return text
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Sanitize plain text input by stripping all HTML.
    Use this for fields that should not contain any HTML.
    """
    if not text:
        return text
    return bleach.clean(text, tags=[], strip=True)
