"""FastAPI application for AI Job Intelligence Platform."""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.config.database import get_db, init_db
from src.utils.logger import api_logger

# Create FastAPI app
app = FastAPI(
    title="AI Job Intelligence Platform",
    description="Intelligent job discovery, matching, and career intelligence system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    api_logger.info("Starting AI Job Intelligence Platform API")
    init_db()
    api_logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Job Intelligence Platform",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Import and include routers
from src.api.routes import jobs, profiles, reports

app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    api_logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)