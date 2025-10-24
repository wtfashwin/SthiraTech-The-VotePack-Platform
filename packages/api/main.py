""" 
The main entry point for the PackVote API server.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import database
import models
import config
from routers import trips, itinerary, polling, expenses, auth, ai, payments

# Define the global API prefix
API_V1_PREFIX = "/api/v1"

# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    models.Base.metadata.create_all(bind=database.engine)
    print("✅ Database tables created")
    
    # Initialize Sentry if configured (placeholder for monitoring)
    if config.settings.SENTRY_DSN:
        # TODO: Initialize Sentry SDK here
        # import sentry_sdk
        # sentry_sdk.init(dsn=config.settings.SENTRY_DSN)
        print("✅ Sentry monitoring enabled")
    
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="PackVote API",
    description="The unified group travel super-app backend - PackVote 3.0",
    version="3.0.0",
    lifespan=lifespan
)

# Add CORS middleware
# Allow both local development and production origins
origins = [
    "http://localhost:5173",  # Local Vite dev server
    "http://localhost:5174",  # Alternative Vite port
    "http://127.0.0.1:5173",  # Alternative localhost
]

# Add production frontend URL from environment variable
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
app.include_router(payments.router, prefix=API_V1_PREFIX)  # Payments router for Stripe integration

# Root health check endpoint
@app.get("/", tags=["Health Check"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "PackVote API is running", "version": "3.0.0"}