import os
from typing import Optional
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Energy Mirror Backend"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./energy_mirror.db")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DEFAULT_INTERVAL_MINUTES: int = 60
    CORS_ORIGINS: list[str] = ["*"]
    DEVICE_INGEST_TOKEN: Optional[str] = os.getenv("DEVICE_INGEST_TOKEN", None)
    ENABLE_HARDWARE_INGEST: bool = os.getenv("ENABLE_HARDWARE_INGEST", "false").lower() == "true"

settings = Settings()
