from pantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings, loaded primarily from environment variables or a .env file.
    Uses pydantic-settings for robust loading and validation.
    """
    
    DATABASE_URL: str
    
    SECRET_KEY: str = "a_very_insecure_default_key_replace_in_prod_32_chars_long"
    
    ALGORITHM: str = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",       
        extra="ignore"         
    )

settings = Settings()

print("--- Loaded Settings ---")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

