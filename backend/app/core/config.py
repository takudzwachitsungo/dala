"""Application configuration"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Project
    PROJECT_NAME: str = "Dala"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct sync database URL for Alembic"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # LLM APIs
    GROQ_API_KEY: str
    MINIMAX_API_KEY: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Conversation Settings
    CONVERSATION_CONTEXT_TTL: int = 3600  # 1 hour in seconds
    MAX_CONTEXT_MESSAGES: int = 5
    
    # Sentiment Analysis
    SENTIMENT_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
