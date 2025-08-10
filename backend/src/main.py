"""
VoltForge FastAPI Application

Main application entry point with structured routing, middleware,
and API endpoint configuration.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
import logging
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api import router as api_router
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.security import SecurityHeadersMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks."""
    logger.info("Starting VoltForge application...")
    
    # Startup tasks
    # TODO: Initialize vector database connection
    # TODO: Initialize Redis connection for job queue
    # TODO: Load component templates
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down VoltForge application...")
    # TODO: Close database connections
    # TODO: Clean up background tasks


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="VoltForge API",
        description="Lightweight tool that transforms user prompts into validated, downloadable KiCad schematic projects",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend dev server
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Add trusted host middleware for production
    if os.getenv("ENVIRONMENT") == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["voltforge.com", "*.voltforge.com"]
        )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Catch-all for non-existent API routes
    @app.get("/api/v1/{path:path}")
    @app.post("/api/v1/{path:path}")
    @app.put("/api/v1/{path:path}")
    @app.delete("/api/v1/{path:path}")
    async def api_catch_all(path: str):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "HTTP_404",
                "message": "Not Found",
                "details": {}
            }
        )
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # If detail is already a dict with error structure, use it directly
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )
        
        # Otherwise, create standard error structure
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": {}
                }
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "service": "voltforge-api"
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )