"""Application configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # App
    APP_NAME: str = "AI Workflow Builder"
    DEBUG: bool = True
    
    # Database - PostgreSQL by default, can be overridden via environment variable or .env file
    # Priority: 1) Environment variable DATABASE_URL, 2) .env file, 3) Default PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_workflow_builder"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # FAISS
    FAISS_INDEX_PATH: str = "./data/faiss"
    
    # LLM Model
    MODEL_NAME: str = "Qwen/Qwen2-0.5B-Instruct"
    MODEL_DEVICE: str = "cpu"


settings = Settings()
