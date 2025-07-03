from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database - SQLite fallback for local development
    DATABASE_URL: str = "sqlite:///./forkplus.db"  # Default to SQLite
    # For PostgreSQL: "postgresql://postgres:admin@123@localhost:5432/forkplus"
    
    # Security
    SECRET_KEY: str = "fork-plus-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Storage
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 16777216  # 16MB
    
    # AI/ML Services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # App Settings
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
