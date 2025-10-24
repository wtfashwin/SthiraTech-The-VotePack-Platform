from pydantic_settings import BaseSettings, SettingsConfigDict
# Removed Pydantic DSN import and replaced it with standard 'str'
# to support SQLAlchemy's driver prefix (e.g., 'postgresql+psycopg2').
from typing import Optional 
# Note: Pydantic v2 is assumed (using model_config, SettingsConfigDict)

# Configuration class using Pydantic BaseSettings.
class Settings(BaseSettings):
    """
    Application settings, loaded primarily from environment variables or a .env file.
    """
    
    # 1. Database Configuration
    # Using 'str' type to accept SQLAlchemy-specific DSN format like 
    # 'postgresql+psycopg2://...' as provided by the user.
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@localhost:5433/packvote"
    
    # 2. Secret Key for security (e.g., JWT signing in FastAPI)
    SECRET_KEY: str = "default_insecure_key_change_me" # Change this immediately in .env
    
    # 3. Algorithm for JWT (if you are using authentication)
    ALGORITHM: str = "HS256"
    
    # 4. Access Token Expiration (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 5. OpenAI API Key for AI features
    OPENAI_API_KEY: Optional[str] = None


    # Inner class to configure Pydantic Settings
    model_config = SettingsConfigDict(
        # Load environment variables from a file named .env
        env_file=".env",
        # Ignore extra fields not defined in the class
        extra="ignore"
    )

# Instantiate the settings object that will be imported in database.py
settings = Settings()

print("Loaded Settings:")
print(f"DB URL: {settings.DATABASE_URL}")
# print(f"Secret Key loaded.")
