from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db.models import TelemetryModel, ApplianceEstimateModel, DetectedEventModel
from app.services.telemetry_service import telemetry_service
from app.api import health, telemetry, ingest, simulator, diagnostics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create SQLite tables if they do not exist
    Base.metadata.create_all(bind=engine)
    # Seed initial history if empty
    db = SessionLocal()
    try:
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
app.include_router(simulator.router, prefix=settings.API_V1_PREFIX)
app.include_router(diagnostics.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_PREFIX}/health",
    }
