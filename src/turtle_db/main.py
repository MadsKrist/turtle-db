"""
FastAPI application entry point for World of Warcraft Items API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from turtle_db.api.v1.router import api_router
from turtle_db.database.connection import create_tables, run_migrations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up turtle-db API...")
    await create_tables()
    logger.info("Database tables created successfully")
    
    # Run migrations to ensure schema is up to date
    try:
        await run_migrations()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.warning(f"Database migrations failed: {e}")
    
    # Seed database with enhanced data
    try:
        from turtle_db.database.enhanced_seed_data import seed_enhanced_database
        await seed_enhanced_database()
        logger.info("Database seeded with enhanced WoW data")
    except Exception as e:
        logger.warning(f"Database seeding failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down turtle-db API...")


# Create FastAPI application
app = FastAPI(
    title="World of Warcraft Items API",
    description="CRUD API for WoW items, recipes, vendors, and professions",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "World of Warcraft Items API",
        "version": "0.1.0",
        "docs": "/docs",
        "api_base": "/api/v1"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "turtle-db"}


def main() -> None:
    """CLI entry point."""
    import uvicorn
    uvicorn.run("turtle_db.main:app", host="0.0.0.0", port=8000, reload=True)