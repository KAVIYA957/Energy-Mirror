"""
config.py - Central Configuration and Security Policy for Energy Mirror.

Hardened for Milestone 2C.14:
- Configurable, environment-aware CORS origin policy replacing permissive wildcards.
- Startup validation to fail safely in production-like configurations.
- Optional administrative API key for appliance registry mutations.
- Constant-time secret comparison and token validation.
- Zero secret leakage in logs, diagnostics, or exceptions.
- Staging mode strictly preserved (ENABLE_HARDWARE_INGEST=false).
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field

DEFAULT_DEV_CORS_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def parse_cors_origins(raw: Optional[str], environment: str) -> List[str]:
    """
    Parse CORS origins from environment variable or apply safe environment defaults.
    In development/testing, defaults to localhost and proxy origins.
    In production, wildcards are forbidden and explicit origins are required.
    """
    if raw is not None and raw.strip():
        # Split on comma, strip whitespace, remove empty entries
        origins = [item.strip() for item in raw.split(",") if item.strip()]
        return origins

    if environment in ("production",):
        return []

    return DEFAULT_DEV_CORS_ORIGINS.copy()


class Settings(BaseModel):
    APP_NAME: str = "Energy Mirror Backend"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    DEBUG: bool = os.getenv("DEBUG", "false" if os.getenv("ENVIRONMENT", "").lower() == "production" else "true").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./energy_mirror.db")
    DEFAULT_INTERVAL_MINUTES: int = 60
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: parse_cors_origins(
            os.getenv("CORS_ORIGINS"),
            os.getenv("ENVIRONMENT", "development").lower(),
        )
    )
    ADMIN_API_KEY: Optional[str] = os.getenv("ADMIN_API_KEY", None)
    DEVICE_INGEST_TOKEN: Optional[str] = os.getenv("DEVICE_INGEST_TOKEN", None)
    ENABLE_HARDWARE_INGEST: bool = os.getenv("ENABLE_HARDWARE_INGEST", "false").lower() == "true"

    def validate_configuration(self):
        """
        Validate critical security and runtime configuration.
        Fails safely and immediately upon invalid or unsafe configuration.
        """
        valid_envs = ("development", "testing", "test", "production")
        if self.ENVIRONMENT not in valid_envs:
            raise ValueError(
                f"Invalid ENVIRONMENT '{self.ENVIRONMENT}'. Permitted values: {valid_envs}."
            )

        # Production security constraints
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                raise ValueError("CRITICAL SECURITY ERROR: DEBUG must be set to false in production mode.")
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CRITICAL SECURITY ERROR: Wildcard '*' CORS origin is strictly forbidden in production mode.")
            if not self.CORS_ORIGINS:
                raise ValueError("CRITICAL SECURITY ERROR: CORS_ORIGINS must contain at least one explicit origin in production mode.")
            if self.ADMIN_API_KEY and len(self.ADMIN_API_KEY) < 16:
                raise ValueError("CRITICAL SECURITY ERROR: ADMIN_API_KEY must be at least 16 characters in production mode.")
            if self.ENABLE_HARDWARE_INGEST and not self.DEVICE_INGEST_TOKEN:
                raise ValueError("CRITICAL SECURITY ERROR: DEVICE_INGEST_TOKEN must be configured when ENABLE_HARDWARE_INGEST is true in production mode.")

        # In any environment, if hardware ingestion is explicitly enabled, a token is mandatory
        if self.ENABLE_HARDWARE_INGEST and not self.DEVICE_INGEST_TOKEN:
            raise ValueError("Configuration Error: ENABLE_HARDWARE_INGEST=true requires DEVICE_INGEST_TOKEN to be configured.")

    def get_sanitized_summary(self) -> dict:
        """
        Returns a sanitized configuration summary safe for logging and diagnostics.
        Guarantees that no raw secrets, keys, or tokens are exposed.
        """
        return {
            "app_name": self.APP_NAME,
            "version": self.APP_VERSION,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "cors_origins_count": len(self.CORS_ORIGINS),
            "cors_origins": self.CORS_ORIGINS,
            "admin_auth_mode": "CONFIGURED_API_KEY" if self.ADMIN_API_KEY else "LOCAL_LOOPBACK_DEV_ONLY",
            "device_ingest_token_configured": bool(self.DEVICE_INGEST_TOKEN),
            "enable_hardware_ingest": self.ENABLE_HARDWARE_INGEST,
        }


settings = Settings()
