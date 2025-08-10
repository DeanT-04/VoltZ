"""
API Contract Tests

Tests to validate API endpoint contracts, request/response schemas,
and error handling behavior.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from backend.src.main import app
from backend.src.models.core import ProjectStatus


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


class TestProjectEndpoints:
    """Test project-related API endpoints."""
    
    def test_create_project_success(self, client):
        """Test successful project creation."""
        request_data = {
            "prompt": "Create a temperature monitoring system with ESP32 and temperature sensor",
            "project_name": "Temperature Monitor"
        }
        
        response = client.post("/api/v1/project", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response schema
        assert "project_id" in data
        assert "parsed_prompt" in data
        assert "status" in data
        
        # Validate project_id format (UUID)
        project_id = data["project_id"]
        assert len(project_id) == 36  # UUID length with hyphens
        assert project_id.count("-") == 4  # UUID has 4 hyphens
        
        # Validate parsed_prompt structure
        parsed_prompt = data["parsed_prompt"]
        assert "project_name" in parsed_prompt
        assert "roles" in parsed_prompt
        assert "constraints" in parsed_prompt
        assert parsed_prompt["project_name"] == "Temperature Monitor"
        
        # Validate status
        assert data["status"] == ProjectStatus.PARSING.value
    
    def test_create_project_minimal_prompt(self, client):
        """Test project creation with minimal prompt."""
        request_data = {
            "prompt": "LED blinker circuit"
        }
        
        response = client.post("/api/v1/project", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should auto-generate project name
        parsed_prompt = data["parsed_prompt"]
        assert "project_name" in parsed_prompt
        assert parsed_prompt["project_name"].startswith("Project")
    
    def test_create_project_invalid_prompt_too_short(self, client):
        """Test project creation with too short prompt."""
        request_data = {
            "prompt": "LED"  # Too short (< 10 chars)
        }
        
        response = client.post("/api/v1/project", json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_create_project_invalid_prompt_too_long(self, client):
        """Test project creation with too long prompt."""
        request_data = {
            "prompt": "x" * 1001  # Too long (> 1000 chars)
        }
        
        response = client.post("/api/v1/project", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_shortlist_success(self, client):
        """Test successful shortlist retrieval."""
        # First create a project
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        # Get shortlist
        response = client.get(f"/api/v1/project/{project_id}/shortlist")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response schema
        assert "project_id" in data
        assert "shortlist" in data
        assert "status" in data
        
        assert data["project_id"] == project_id
        assert data["status"] == ProjectStatus.RESEARCHING.value
        
        # Validate shortlist structure
        shortlist = data["shortlist"]
        assert isinstance(shortlist, dict)
        
        # Should have component roles
        for role, components in shortlist.items():
            assert isinstance(components, list)
            for component in components:
                # Validate component schema
                assert "mpn" in component
                assert "manufacturer" in component
                assert "description" in component
                assert "datasheet_url" in component
                assert "datasheet_ref" in component
                assert "pins" in component
                assert "electrical_specs" in component
    
    def test_get_shortlist_project_not_found(self, client):
        """Test shortlist retrieval for non-existent project."""
        response = client.get("/api/v1/project/non-existent-id/shortlist")
        
        assert response.status_code == 404
        data = response.json()
        
        # Validate error response schema
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
        assert error["code"] == "PROJECT_NOT_FOUND"
    
    def test_select_components_success(self, client):
        """Test successful component selection."""
        # Create project and get shortlist
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        # Get shortlist to see available components
        shortlist_response = client.get(f"/api/v1/project/{project_id}/shortlist")
        shortlist = shortlist_response.json()["shortlist"]
        
        # Select first component from each role
        selections = {}
        for role, components in shortlist.items():
            if components:
                selections[role] = components[0]["mpn"]
        
        # Make selection
        response = client.post(
            f"/api/v1/project/{project_id}/select",
            json={"selections": selections}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response schema
        assert "project_id" in data
        assert "selections" in data
        assert "schematic" in data
        assert "status" in data
        
        assert data["project_id"] == project_id
        assert data["selections"] == selections
        assert data["status"] == ProjectStatus.GENERATING.value
        
        # Validate schematic structure
        schematic = data["schematic"]
        if schematic:  # May be None for async processing
            assert "svg_preview" in schematic
            assert "kicad_sexpr" in schematic
            assert "netlist" in schematic
            assert "warnings" in schematic
            assert "bom" in schematic
    
    def test_select_components_invalid_role(self, client):
        """Test component selection with invalid role."""
        # Create project
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        # Get shortlist first
        client.get(f"/api/v1/project/{project_id}/shortlist")
        
        # Try to select component for non-existent role
        response = client.post(
            f"/api/v1/project/{project_id}/select",
            json={"selections": {"invalid_role": "ESP32-WROOM-32"}}
        )
        
        assert response.status_code == 400
        data = response.json()
        
        error = data["error"]
        assert error["code"] == "INVALID_ROLE"
        assert "available_roles" in error["details"]
    
    def test_select_components_invalid_mpn(self, client):
        """Test component selection with invalid MPN."""
        # Create project and get shortlist
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        shortlist_response = client.get(f"/api/v1/project/{project_id}/shortlist")
        shortlist = shortlist_response.json()["shortlist"]
        
        # Get a valid role but use invalid MPN
        valid_role = list(shortlist.keys())[0]
        
        response = client.post(
            f"/api/v1/project/{project_id}/select",
            json={"selections": {valid_role: "INVALID-MPN"}}
        )
        
        assert response.status_code == 400
        data = response.json()
        
        error = data["error"]
        assert error["code"] == "INVALID_COMPONENT_SELECTION"
        assert "available_components" in error["details"]
    
    def test_export_project_success(self, client):
        """Test successful project export."""
        # Create project, get shortlist, and select components
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        # Get shortlist and select components
        shortlist_response = client.get(f"/api/v1/project/{project_id}/shortlist")
        shortlist = shortlist_response.json()["shortlist"]
        
        selections = {}
        for role, components in shortlist.items():
            if components:
                selections[role] = components[0]["mpn"]
        
        client.post(f"/api/v1/project/{project_id}/select", json={"selections": selections})
        
        # Export project
        response = client.get(f"/api/v1/project/{project_id}/export")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response schema
        assert "project_id" in data
        assert "download_url" in data
        assert "format" in data
        assert "file_size" in data
        
        assert data["project_id"] == project_id
        assert data["format"] == "kicad"
        assert isinstance(data["file_size"], int)
        assert data["file_size"] > 0
    
    def test_export_project_unsupported_format(self, client):
        """Test export with unsupported format."""
        # Create and prepare project
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        response = client.get(f"/api/v1/project/{project_id}/export?format=eagle")
        
        assert response.status_code == 400
        data = response.json()
        
        error = data["error"]
        assert error["code"] == "UNSUPPORTED_FORMAT"
        assert "supported_formats" in error["details"]
    
    def test_export_project_not_generated(self, client):
        """Test export before schematic generation."""
        # Create project but don't generate schematic
        create_response = client.post("/api/v1/project", json={
            "prompt": "Temperature monitoring with ESP32"
        })
        project_id = create_response.json()["project_id"]
        
        response = client.get(f"/api/v1/project/{project_id}/export")
        
        assert response.status_code == 400
        data = response.json()
        
        error = data["error"]
        assert error["code"] == "SCHEMATIC_NOT_GENERATED"


class TestJobEndpoints:
    """Test job-related API endpoints."""
    
    def test_get_job_status_not_found(self, client):
        """Test job status retrieval for non-existent job."""
        response = client.get("/api/v1/job/non-existent-job-id")
        
        assert response.status_code == 404
        data = response.json()
        
        # Validate error response schema
        assert "error" in data
        error = data["error"]
        assert error["code"] == "JOB_NOT_FOUND"


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "service" in data
        
        assert data["status"] == "healthy"
        assert data["service"] == "voltforge-api"


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_security_headers(self, client):
        """Test that security headers are added to responses."""
        response = client.get("/health")
        
        # Check for security headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
        
        # Validate header values
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
    
    def test_rate_limiting_headers(self, client):
        """Test that rate limiting headers are added."""
        response = client.post("/api/v1/project", json={
            "prompt": "Test circuit with LED"
        })
        
        # Check for rate limiting headers
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert "X-RateLimit-Limit-Hour" in response.headers
        assert "X-RateLimit-Remaining-Minute" in response.headers
        assert "X-RateLimit-Remaining-Hour" in response.headers
        
        # Validate header values are numeric
        assert int(response.headers["X-RateLimit-Limit-Minute"]) > 0
        assert int(response.headers["X-RateLimit-Limit-Hour"]) > 0
    
    def test_cors_headers(self, client):
        """Test CORS headers for cross-origin requests."""
        # Make an OPTIONS request to test CORS
        response = client.options(
            "/api/v1/project",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Should allow the request
        assert response.status_code in [200, 204]


class TestErrorHandling:
    """Test error handling and response formats."""
    
    def test_404_error_format(self, client):
        """Test 404 error response format."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        
        # Should have error structure
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
    
    def test_validation_error_format(self, client):
        """Test validation error response format."""
        # Send invalid JSON
        response = client.post("/api/v1/project", json={})
        
        assert response.status_code == 422
        data = response.json()
        
        # FastAPI validation errors have different format
        assert "detail" in data