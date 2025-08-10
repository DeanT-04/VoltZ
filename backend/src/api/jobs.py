"""
Job API endpoints

Handles background job status tracking and management.
"""

from typing import Dict, Any, Optional
from enum import Enum
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResult(BaseModel):
    """Job result data."""
    data: Optional[Dict[str, Any]] = Field(None, description="Job result data")
    error: Optional[str] = Field(None, description="Error message if job failed")


class JobResponse(BaseModel):
    """Response schema for job status."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Job progress percentage")
    result: Optional[JobResult] = Field(None, description="Job result if completed")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


# In-memory job storage for MVP (TODO: Replace with Redis)
_jobs: Dict[str, Dict[str, Any]] = {}


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    """
    Get the status of a background job.
    
    Returns current status, progress, and results for long-running operations
    like schematic generation and component research.
    
    Requirements: 1.4 (job status tracking), 2.3 (background processing)
    """
    try:
        # Retrieve job from storage
        job_data = _jobs.get(job_id)
        if not job_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job {job_id} not found",
                    "details": {}
                }
            )
        
        logger.info(f"Retrieved status for job {job_id}: {job_data['status']}")
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus(job_data["status"]),
            progress=job_data.get("progress"),
            result=JobResult(
                data=job_data.get("result"),
                error=job_data.get("error")
            ) if job_data.get("result") or job_data.get("error") else None,
            created_at=job_data["created_at"],
            updated_at=job_data["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "JOB_STATUS_RETRIEVAL_FAILED",
                "message": "Failed to retrieve job status",
                "details": {"error": str(e)}
            }
        )