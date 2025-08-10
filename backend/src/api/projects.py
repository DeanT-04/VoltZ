"""
Project API endpoints

Handles project creation, component shortlisting, selection, and export.
"""

from typing import Dict, List, Any, Optional
from uuid import uuid4
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..models.core import Project, ParsedPrompt, Component, SchematicResult, ProjectStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response schemas
class CreateProjectRequest(BaseModel):
    """Request schema for creating a new project."""
    prompt: str = Field(..., min_length=10, max_length=1000, description="Natural language circuit description")
    project_name: Optional[str] = Field(None, max_length=100, description="Optional project name")


class CreateProjectResponse(BaseModel):
    """Response schema for project creation."""
    project_id: str = Field(..., description="Unique project identifier")
    parsed_prompt: ParsedPrompt = Field(..., description="Parsed prompt with roles and constraints")
    status: ProjectStatus = Field(..., description="Current project status")


class ShortlistResponse(BaseModel):
    """Response schema for component shortlist."""
    project_id: str = Field(..., description="Project identifier")
    shortlist: Dict[str, List[Component]] = Field(..., description="Component candidates by role")
    status: ProjectStatus = Field(..., description="Current project status")


class SelectComponentsRequest(BaseModel):
    """Request schema for component selection."""
    selections: Dict[str, str] = Field(..., description="Selected component MPNs by role")


class SelectComponentsResponse(BaseModel):
    """Response schema for component selection."""
    project_id: str = Field(..., description="Project identifier")
    selections: Dict[str, str] = Field(..., description="Selected components")
    schematic: Optional[SchematicResult] = Field(None, description="Generated schematic if available")
    status: ProjectStatus = Field(..., description="Current project status")


class ExportResponse(BaseModel):
    """Response schema for project export."""
    project_id: str = Field(..., description="Project identifier")
    download_url: str = Field(..., description="URL to download the KiCad project zip")
    format: str = Field(..., description="Export format (kicad)")
    file_size: int = Field(..., description="File size in bytes")


# In-memory storage for MVP (TODO: Replace with proper database)
_projects: Dict[str, Project] = {}


@router.post("", response_model=CreateProjectResponse)
async def create_project(request: CreateProjectRequest) -> CreateProjectResponse:
    """
    Create a new project from a natural language prompt.
    
    This endpoint parses the user's prompt to extract component roles and constraints,
    then initiates the component research process.
    
    Requirements: 1.2 (API responses ≤150ms), 6.1 (input sanitization)
    """
    try:
        # Generate unique project ID
        project_id = str(uuid4())
        
        # TODO: Implement actual prompt parsing with PlannerService
        # For now, create a stub parsed prompt
        parsed_prompt = ParsedPrompt(
            project_name=request.project_name or f"Project {project_id[:8]}",
            roles={
                "microcontroller": "ESP32",  # Stub data
                "sensor": "temperature"
            },
            constraints={
                "max_voltage": 5.0,
                "min_battery": "LiPo"
            }
        )
        
        # Create project
        project = Project(
            id=project_id,
            name=parsed_prompt.project_name,
            prompt=parsed_prompt,
            shortlist={},
            selections={},
            schematic=None,
            status=ProjectStatus.PARSING
        )
        
        # Store project (in-memory for MVP)
        _projects[project_id] = project
        
        logger.info(f"Created project {project_id} with prompt: {request.prompt[:50]}...")
        
        return CreateProjectResponse(
            project_id=project_id,
            parsed_prompt=parsed_prompt,
            status=project.status
        )
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROJECT_CREATION_FAILED",
                "message": "Failed to create project",
                "details": {"error": str(e)}
            }
        )


@router.get("/{project_id}/shortlist", response_model=ShortlistResponse)
async def get_shortlist(project_id: str) -> ShortlistResponse:
    """
    Get component shortlist for a project.
    
    Returns a list of component candidates for each role identified in the prompt.
    Components are sourced from local vector database and external APIs.
    
    Requirements: 1.2 (API responses ≤150ms), 7.1 (local vector database first)
    """
    try:
        # Retrieve project
        project = _projects.get(project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "PROJECT_NOT_FOUND",
                    "message": f"Project {project_id} not found",
                    "details": {}
                }
            )
        
        # TODO: Implement actual component research with ResearcherService
        # For now, return stub shortlist
        if not project.shortlist:
            # Generate stub shortlist
            project.shortlist = {
                "microcontroller": [
                    Component(
                        mpn="ESP32-WROOM-32",
                        manufacturer="Espressif",
                        description="WiFi & Bluetooth MCU Module",
                        category="microcontroller",
                        datasheet_url="https://example.com/esp32-datasheet.pdf",
                        datasheet_ref="esp32_v3.2",
                        pins={
                            "VCC": "power",
                            "GND": "ground",
                            "GPIO2": "GPIO",
                            "GPIO4": "GPIO"
                        },
                        electrical_specs={
                            "supply_voltage": "3.3V",
                            "max_current": "240mA"
                        }
                    )
                ],
                "sensor": [
                    Component(
                        mpn="TMP117",
                        manufacturer="Texas Instruments",
                        description="High-Precision Digital Temperature Sensor",
                        category="sensor",
                        datasheet_url="https://example.com/tmp117-datasheet.pdf",
                        datasheet_ref="tmp117_v1.1",
                        pins={
                            "VDD": "power",
                            "GND": "ground",
                            "SDA": "i2c_data",
                            "SCL": "i2c_clock"
                        },
                        electrical_specs={
                            "supply_voltage": "1.8V-5.5V",
                            "max_current": "3.5µA"
                        }
                    )
                ]
            }
            project.status = ProjectStatus.RESEARCHING
        
        logger.info(f"Retrieved shortlist for project {project_id}")
        
        return ShortlistResponse(
            project_id=project_id,
            shortlist=project.shortlist,
            status=project.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shortlist for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "SHORTLIST_RETRIEVAL_FAILED",
                "message": "Failed to retrieve component shortlist",
                "details": {"error": str(e)}
            }
        )


@router.post("/{project_id}/select", response_model=SelectComponentsResponse)
async def select_components(
    project_id: str, 
    request: SelectComponentsRequest
) -> SelectComponentsResponse:
    """
    Select components from shortlist and generate schematic.
    
    Updates the project with user's component selections and triggers
    schematic generation using SKiDL templates.
    
    Requirements: 1.3 (generate valid KiCad schematic), 1.4 (SVG preview ≤2-5s)
    """
    try:
        # Retrieve project
        project = _projects.get(project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "PROJECT_NOT_FOUND",
                    "message": f"Project {project_id} not found",
                    "details": {}
                }
            )
        
        # Validate selections against shortlist
        if not project.shortlist:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "NO_SHORTLIST_AVAILABLE",
                    "message": "No component shortlist available for selection",
                    "details": {}
                }
            )
        
        # Validate that all selected components exist in shortlist
        for role, mpn in request.selections.items():
            if role not in project.shortlist:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_ROLE",
                        "message": f"Role '{role}' not found in shortlist",
                        "details": {"available_roles": list(project.shortlist.keys())}
                    }
                )
            
            # Check if MPN exists in the role's shortlist
            available_mpns = [comp.mpn for comp in project.shortlist[role]]
            if mpn not in available_mpns:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_COMPONENT_SELECTION",
                        "message": f"Component '{mpn}' not available for role '{role}'",
                        "details": {"available_components": available_mpns}
                    }
                )
        
        # Update project selections
        project.selections = request.selections
        project.status = ProjectStatus.SELECTING
        
        # TODO: Implement actual schematic generation with SKiDLCoderService
        # For now, return stub schematic result
        project.schematic = SchematicResult(
            svg_preview="<svg><!-- Stub SVG preview --></svg>",
            kicad_sexpr="(kicad_sch (version 20230121) (generator eeschema))",
            netlist="# Stub netlist",
            warnings=["This is a stub implementation"],
            bom=[]
        )
        project.status = ProjectStatus.GENERATING
        
        logger.info(f"Selected components for project {project_id}: {request.selections}")
        
        return SelectComponentsResponse(
            project_id=project_id,
            selections=project.selections,
            schematic=project.schematic,
            status=project.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting components for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "COMPONENT_SELECTION_FAILED",
                "message": "Failed to select components",
                "details": {"error": str(e)}
            }
        )


@router.get("/{project_id}/export", response_model=ExportResponse)
async def export_project(
    project_id: str,
    format: str = Query("kicad", description="Export format (currently only 'kicad' supported)")
) -> ExportResponse:
    """
    Export project as downloadable KiCad package.
    
    Generates a zip file containing KiCad schematic files, BOM, and project metadata.
    
    Requirements: 1.5 (downloadable zip with KiCad files), 4.5 (KiCad compatibility)
    """
    try:
        # Validate format
        if format != "kicad":
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "UNSUPPORTED_FORMAT",
                    "message": f"Export format '{format}' not supported",
                    "details": {"supported_formats": ["kicad"]}
                }
            )
        
        # Retrieve project
        project = _projects.get(project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "PROJECT_NOT_FOUND",
                    "message": f"Project {project_id} not found",
                    "details": {}
                }
            )
        
        # Check if project has generated schematic
        if not project.schematic or project.status not in [ProjectStatus.GENERATING, ProjectStatus.COMPLETED]:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "SCHEMATIC_NOT_GENERATED",
                    "message": "Project schematic has not been generated yet",
                    "details": {"current_status": project.status.value}
                }
            )
        
        # TODO: Implement actual export with ExportService
        # For now, return stub export response
        download_url = f"/api/v1/project/{project_id}/download/{format}"
        
        logger.info(f"Exported project {project_id} in {format} format")
        
        return ExportResponse(
            project_id=project_id,
            download_url=download_url,
            format=format,
            file_size=1024  # Stub file size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXPORT_FAILED",
                "message": "Failed to export project",
                "details": {"error": str(e)}
            }
        )