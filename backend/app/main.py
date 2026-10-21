from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db.models import TelemetryModel, ApplianceEstimateModel, DetectedEventModel
from app.services.telemetry_service import telemetry_service
from app.services.appliance_registry import appliance_registry
from app.services.simulator import simulator
from app.services.event_detector import event_detector
from app.api import health, telemetry, ingest, simulator as sim_router, diagnostics, appliances

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create SQLite tables if they do not exist
    Base.metadata.create_all(bind=engine)
    # Seed appliance registry and initial history if empty
    db = SessionLocal()
    try:
        appliance_registry.seed_defaults(db)
        simulator.sync_from_registry(db)
        event_detector.sync_from_registry(db)
        telemetry_service.seed_initial_history(db)
    finally:
        db.close()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Energy Mirror backend API: Ingestion, telemetry simulation, and NILM disaggregation.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under /api/v1
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(telemetry.router, prefix=settings.API_V1_PREFIX)
app.include_router(ingest.router, prefix=settings.API_V1_PREFIX)
app.include_router(sim_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(diagnostics.router, prefix=settings.API_V1_PREFIX)
app.include_router(appliances.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_PREFIX}/health",
    }
