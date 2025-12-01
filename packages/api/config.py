from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import secrets

class Settings(BaseSettings):
    """
    Application settings, loaded primarily from environment variables or a .env file.
    Uses pydantic-settings for robust loading and validation.
    """

    # 1. Database Configuration
    DATABASE_URL: str

    # 2. Security & JWT
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "a_very_insecure_default_key_replace_in_prod_32_chars_long":
            raise ValueError("Must set a secure SECRET_KEY in environment variables")
        return v
    
    # 3. AI API Key (Gemini)
    GEMINI_API_KEY: Optional[str] = None
    
    # 4. Payments (Stripe)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # 5. Monitoring (Sentry)
    SENTRY_DSN: Optional[str] = None
    
    # 6. Frontend URL for CORS and redirects
    FRONTEND_URL: str = "http://localhost:5173"

    # 7. Redis Cache URL (Upstash free tier)
    REDIS_URL: Optional[str] = None

    # 8. Email Service (Brevo free tier)
    BREVO_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",       # Load from .env file if it exists
        extra="ignore"         # Ignore extra environment variables
    )

settings = Settings() # type: ignore[call-arg]

print("--- Loaded Settings ---")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

