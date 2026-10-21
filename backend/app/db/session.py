"""
session.py - Database Session and Engine Configuration for Energy Mirror.

Supports both SQLite (default for local development and demo) and PostgreSQL
(for production and scalable deployment) via DATABASE_URL:
- Automatically normalizes postgres:// to postgresql+psycopg2://
- Configures SQLite with check_same_thread=False
- Configures PostgreSQL with pool_pre_ping=True, pool_size, and max_overflow
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


def normalize_database_url(url: str) -> str:
    """
    Normalizes database connection URLs for SQLAlchemy 2.0+ and psycopg2:
    - Normalizes legacy 'postgres://' to 'postgresql+psycopg2://'
    - Ensures standard 'postgresql://' specifies the psycopg2 driver
    """
    if not url:
        return "sqlite:///./energy_mirror.db"

    clean_url = url.strip()
    if clean_url.startswith("postgres://"):
        return clean_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if clean_url.startswith("postgresql://") and not clean_url.startswith("postgresql+"):
        return clean_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return clean_url


DATABASE_URL = normalize_database_url(settings.DATABASE_URL)

engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL / production connection pool settings
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for yielding database sessions with automatic closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
