from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_MB: int = 20
    ALERT_LEAD_DAYS: int = 7
    BACKUP_DIR: str = "/home/tony/docker/loan-tracker/backups"
    DEFAULT_CURRENCY: str = "INR"
    ENVIRONMENT: str = "production"

    class Config:
        env_file = ".env"

settings = Settings()
