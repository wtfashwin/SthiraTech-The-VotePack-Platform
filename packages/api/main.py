"""
The main entry point for the PackVote API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import database
import models
from routers import trips, itinerary, polling, expenses, auth, ai

# Define the global API prefix
API_V1_PREFIX = "/api/v1"

# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    models.Base.metadata.create_all(bind=database.engine)
    print("✅ Database tables created")
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="PackVote API",
    description="The unified group travel super-app backend.",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Added both common Vite ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API prefix
app.include_router(auth.router, prefix=API_V1_PREFIX)  # Auth router first (no authentication required)
app.include_router(trips.router, prefix=API_V1_PREFIX)
app.include_router(itinerary.router, prefix=API_V1_PREFIX)
app.include_router(polling.router, prefix=API_V1_PREFIX)
app.include_router(expenses.router, prefix=API_V1_PREFIX)
app.include_router(ai.router, prefix=API_V1_PREFIX)  # AI router for semantic search

# Root health check endpoint
@app.get("/", tags=["Health Check"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "PackVote API is running", "version": "2.0.0"}