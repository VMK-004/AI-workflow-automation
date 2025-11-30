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
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_workflow_builder.db"
    
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
