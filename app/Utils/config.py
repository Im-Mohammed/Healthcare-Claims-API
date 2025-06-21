from pydantic_settings import BaseSettings
import os
from app.Utils.logger import setup_logger

# Set up logger
logger = setup_logger()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./healthcare_claims.db"
    SECRET_KEY: str = "Your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

# Load settings
settings = Settings()

# Log that settings were loaded successfully (without exposing secrets)
logger.info("Application settings loaded.")
logger.debug(f"DATABASE_URL: {settings.DATABASE_URL}")
logger.debug(f"REDIS_URL: {settings.REDIS_URL}")
logger.debug(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
