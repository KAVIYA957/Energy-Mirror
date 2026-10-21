"""
test_database_and_migrations.py - Database and Alembic Migration Tests for Milestone 2C.15.

Tests:
1. URL normalization for PostgreSQL (postgres:// and postgresql:// -> postgresql+psycopg2://).
2. SQLite connection argument isolation (check_same_thread=False for SQLite only).
3. Alembic migration upgrade from a completely empty database.
4. Migration idempotency and repeat upgrades.
5. Alembic downgrade to base and re-upgrade to head.
6. Seeding appliance registry and persisting events on an Alembic-migrated database.
7. Diagnostics database_type reporting (SQLite vs PostgreSQL).
8. Data integrity across migration and seeding lifecycle.
"""

import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from app.db.session import normalize_database_url
from app.services.appliance_registry import appliance_registry
from app.services.telemetry_service import telemetry_service
from app.services.simulator import DetectedEvent
from datetime import datetime


BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALEMBIC_INI_PATH = os.path.join(BACKEND_DIR, "alembic.ini")


class TestDatabaseUrlNormalization:
    """Tests URL normalization for SQLAlchemy and driver compatibility."""

    def test_legacy_postgres_url_normalized(self):
        url = "postgres://usr:pwd@dbhost:5432/em_db"
        norm = normalize_database_url(url)
        assert norm == "postgresql+psycopg2://usr:pwd@dbhost:5432/em_db"

    def test_standard_postgresql_url_normalized_to_psycopg2(self):
        url = "postgresql://usr:pwd@dbhost:5432/em_db"
        norm = normalize_database_url(url)
        assert norm == "postgresql+psycopg2://usr:pwd@dbhost:5432/em_db"

    def test_explicit_driver_postgresql_url_preserved(self):
        url = "postgresql+psycopg2://usr:pwd@dbhost:5432/em_db"
        norm = normalize_database_url(url)
        assert norm == "postgresql+psycopg2://usr:pwd@dbhost:5432/em_db"

    def test_sqlite_url_preserved(self):
        url = "sqlite:///./energy_mirror.db"
        norm = normalize_database_url(url)
        assert norm == "sqlite:///./energy_mirror.db"

    def test_empty_or_none_url_fallback(self):
        assert normalize_database_url("") == "sqlite:///./energy_mirror.db"
        assert normalize_database_url(None) == "sqlite:///./energy_mirror.db"


class TestAlembicMigrations:
    """Tests programmatic Alembic migrations on fresh databases."""

    @pytest.fixture
    def temp_db_path(self):
        import gc
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        if os.path.exists(path):
            os.remove(path)
        yield path
        gc.collect()
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

    def get_alembic_config(self, db_url: str) -> Config:
        cfg = Config(ALEMBIC_INI_PATH)
        cfg.set_main_option("sqlalchemy.url", db_url)
        cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
        return cfg

    def test_upgrade_from_empty_database(self, temp_db_path):
        """Verify upgrading from an empty database generates all expected tables and indexes."""
        db_url = f"sqlite:///{temp_db_path.replace(os.sep, '/')}"
        cfg = self.get_alembic_config(db_url)

        # 1. Run upgrade to head on empty database
        command.upgrade(cfg, "head")

        # 2. Inspect created tables
        engine = create_engine(db_url)
        try:
            inspector = inspect(engine)
            tables = set(inspector.get_table_names())

            expected_tables = {
                "alembic_version",
                "telemetry_records",
                "appliance_estimates",
                "detected_events",
                "appliance_definitions",
            }
            assert expected_tables.issubset(tables)

            # 3. Check appliance_definitions columns and indexes
            cols = {c["name"] for c in inspector.get_columns("appliance_definitions")}
            assert {"id", "appliance_id", "name", "nominal_power_w", "detection_capability"}.issubset(cols)

            # Check unique constraint on appliance_id
            indexes = inspector.get_indexes("appliance_definitions")
            app_id_idx = next((i for i in indexes if i["name"] == "ix_appliance_definitions_appliance_id"), None)
            assert app_id_idx is not None
            assert bool(app_id_idx["unique"]) is True
        finally:
            engine.dispose()

    def test_repeat_upgrade_idempotency(self, temp_db_path):
        """Repeated upgrade commands on a current database must succeed idempotently."""
        db_url = f"sqlite:///{temp_db_path.replace(os.sep, '/')}"
        cfg = self.get_alembic_config(db_url)

        command.upgrade(cfg, "head")
        # Second run should be a no-op and not fail
        command.upgrade(cfg, "head")

    def test_downgrade_and_reupgrade_cycle(self, temp_db_path):
        """Verify clean downgrade to base and re-upgrade to head."""
        db_url = f"sqlite:///{temp_db_path.replace(os.sep, '/')}"
        cfg = self.get_alembic_config(db_url)

        # Upgrade
        command.upgrade(cfg, "head")
        engine = create_engine(db_url)
        inspector = inspect(engine)
        assert "appliance_definitions" in inspector.get_table_names()

        # Downgrade to base
        command.downgrade(cfg, "base")
        inspector = inspect(engine)
        assert "appliance_definitions" not in inspector.get_table_names()
        assert "telemetry_records" not in inspector.get_table_names()

        # Re-upgrade
        command.upgrade(cfg, "head")
        inspector = inspect(engine)
        assert "appliance_definitions" in inspector.get_table_names()
        assert "telemetry_records" in inspector.get_table_names()

        engine.dispose()

    def test_seeding_and_persistence_on_migrated_db(self, temp_db_path):
        """Verify seeding defaults and recording events works on an Alembic-migrated database."""
        db_url = f"sqlite:///{temp_db_path.replace(os.sep, '/')}"
        cfg = self.get_alembic_config(db_url)
        command.upgrade(cfg, "head")

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 1. Seed defaults
            seeded = appliance_registry.seed_defaults(session)
            assert len(seeded) == 4
            all_apps = appliance_registry.get_all(session)
            assert len(all_apps) == 4

            # 2. Re-seed idempotency
            re_seeded = appliance_registry.seed_defaults(session)
            assert len(re_seeded) == 0
            assert len(appliance_registry.get_all(session)) == 4

            # 3. Persist detected event
            ev = DetectedEvent(
                status="MATCHED",
                appliance_id="heater_01",
                appliance_name="Water Heater",
                transition_type="ON",
                delta_power_w=140.0,
                delta_pf=0.01,
                rule_description="Test event on migrated db",
                timestamp=datetime.utcnow(),
                data_classification="RULE_BASED_ESTIMATE",
            )
            persisted = telemetry_service.persist_detected_event(session, ev)
            assert persisted is not None
            assert persisted.appliance_id == "heater_01"

            # 4. Duplicate event check (idempotent deduplication)
            dup = telemetry_service.persist_detected_event(session, ev)
            assert dup.id == persisted.id
        finally:
            session.close()
            engine.dispose()


class TestDiagnosticsDatabaseType:
    """Verifies diagnostics reports database_type dynamically."""

    def test_diagnostics_reports_sqlite_by_default(self, client):
        resp = client.get("/api/v1/diagnostics/system")
        assert resp.status_code == 200
        assert resp.json()["database_type"] == "SQLite"

    def test_diagnostics_reports_postgresql_when_configured(self, client):
        from unittest.mock import patch
        with patch("app.api.diagnostics.settings.DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/em_db"):
            resp = client.get("/api/v1/diagnostics/system")
            assert resp.status_code == 200
            assert resp.json()["database_type"] == "PostgreSQL"
