import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure backend root is on sys.path for app module imports
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.config import settings
from app.db.session import Base, normalize_database_url
# Explicitly import all models to register them in Base.metadata
from app.db.models import (
    TelemetryModel,
    ApplianceEstimateModel,
    DetectedEventModel,
    ApplianceDefinitionModel,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_effective_url() -> str:
    """
    Resolve effective database URL for migrations:
    1. CLI argument '-x url=...' if provided
    2. Explicit programmatic override in alembic Config ('sqlalchemy.url')
    3. settings.DATABASE_URL from application configuration
    4. Default fallback: sqlite:///./energy_mirror.db
    """
    cmd_url = context.get_x_argument(as_dictionary=True).get("url")
    if cmd_url and cmd_url.strip():
        return normalize_database_url(cmd_url.strip())

    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url and ini_url.strip() and "driver://user:pass" not in ini_url:
        return normalize_database_url(ini_url.strip())

    if settings.DATABASE_URL and settings.DATABASE_URL.strip():
        return normalize_database_url(settings.DATABASE_URL.strip())

    return "sqlite:///./energy_mirror.db"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without an active DB connection."""
    url = get_effective_url()
    is_sqlite = url.startswith("sqlite")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with an active engine connection."""
    url = get_effective_url()
    is_sqlite = url.startswith("sqlite")

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connect_args = {}
    if is_sqlite:
        connect_args["check_same_thread"] = False

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
