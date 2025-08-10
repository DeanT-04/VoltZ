"""
VoltForge API Package

Contains all API routes and endpoint implementations.
"""

from fastapi import APIRouter

from .projects import router as projects_router
from .jobs import router as jobs_router

# Main API router
router = APIRouter()

# Include sub-routers
router.include_router(projects_router, prefix="/project", tags=["projects"])
router.include_router(jobs_router, prefix="/job", tags=["jobs"])