from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import courses_router, universities_router, health_router
from app.jobs.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting UniGuide AI API...")
    init_db()
    logger.info("Database initialized")

    # Start background scheduler
    start_scheduler()
    logger.info("Background scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down...")
    stop_scheduler()
    logger.info("Background scheduler stopped")


app = FastAPI(
    title="UniGuide AI API",
    description="API for UK university course data and admission predictions",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(courses_router)
app.include_router(universities_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to UniGuide AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
