import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.session as db_session_module
import app.main as app_main_module
from app.db.session import Base, get_db
from app.main import app
from app.services.telemetry_service import telemetry_service

# Dedicated, isolated in-memory SQLite engine
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def patch_db_engine():
    """
    Patch the global database engine and sessionmaker across app modules for the entire test session.
    This guarantees that neither app startup lifespan nor direct imports ever touch energy_mirror.db.
    """
    orig_db_engine = db_session_module.engine
    orig_db_session_local = db_session_module.SessionLocal
    orig_main_engine = app_main_module.engine
    orig_main_session = app_main_module.SessionLocal

    db_session_module.engine = test_engine
    db_session_module.SessionLocal = TestingSessionLocal
    app_main_module.engine = test_engine
    app_main_module.SessionLocal = TestingSessionLocal

    yield

    db_session_module.engine = orig_db_engine
    db_session_module.SessionLocal = orig_db_session_local
    app_main_module.engine = orig_main_engine
    app_main_module.SessionLocal = orig_main_session


@pytest.fixture(scope="function")
def db_session():
    """
    Create fresh database schema and seed deterministic history for each test function.
    Drops all tables after test completion to ensure 100% test-to-test isolation.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        telemetry_service.seed_initial_history(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provide a FastAPI TestClient strictly bound to the isolated in-memory test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_simulator_state():
    """
    Ensure every test function starts and finishes with pristine baseline simulator state.
    Prevents virtual appliance toggle leaks across backend test suites.
    """
    from app.services.simulator import simulator
    simulator.reset()
    yield
    simulator.reset()
