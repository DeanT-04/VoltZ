"""Core data models for VoltForge."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    
    CREATED = "created"
    PARSING = "parsing"
    RESEARCHING = "researching"
    SELECTING = "selecting"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"


class ParsedPrompt(BaseModel):
    """Parsed user prompt with extracted roles and constraints."""
    
    project_name: str = Field(..., min_length=1, max_length=100)
    roles: Dict[str, str] = Field(
        default_factory=dict,
        description="Component roles extracted from prompt"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Technical constraints extracted from prompt"
    )
    
    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate project name contains only safe characters."""
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        
        # Allow alphanumeric, spaces, hyphens, underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Project name contains invalid characters")
        
        return v.strip()
    
    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate component roles."""
        valid_roles = {
            "microcontroller", "sensor", "power", "actuator", 
            "communication", "display", "memory", "analog"
        }
        
        for role in v.keys():
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}")
        
        return v
    
    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technical constraints."""
        # Validate voltage constraints
        if "max_voltage" in v:
            voltage = v["max_voltage"]
            if not isinstance(voltage, (int, float)) or voltage <= 0 or voltage > 50:
                raise ValueError("max_voltage must be between 0 and 50V")
        
        if "min_voltage" in v:
            voltage = v["min_voltage"]
            if not isinstance(voltage, (int, float)) or voltage <= 0 or voltage > 50:
                raise ValueError("min_voltage must be between 0 and 50V")
        
        # Validate size constraints
        if "max_size" in v:
            size = v["max_size"]
            if not isinstance(size, str) or size not in ["small", "medium", "large"]:
                raise ValueError("max_size must be 'small', 'medium', or 'large'")
        
        return v


class Component(BaseModel):
    """Electronic component with specifications and pin mapping."""
    
    mpn: str = Field(..., min_length=1, max_length=50, description="Manufacturer Part Number")
    manufacturer: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    datasheet_url: Optional[str] = Field(None, max_length=500)
    datasheet_ref: Optional[str] = Field(None, max_length=100)
    pins: Dict[str, str] = Field(
        default_factory=dict,
        description="Pin name to function mapping"
    )
    electrical_specs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Electrical specifications"
    )
    category: str = Field(..., min_length=1, max_length=50)
    
    @field_validator("mpn")
    @classmethod
    def validate_mpn(cls, v: str) -> str:
        """Validate manufacturer part number."""
        if not v.strip():
            raise ValueError("MPN cannot be empty")
        
        # Allow alphanumeric, hyphens, underscores, dots
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        if not all(c in allowed_chars for c in v):
            raise ValueError("MPN contains invalid characters")
        
        return v.strip().upper()
    
    @field_validator("pins")
    @classmethod
    def validate_pins(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate pin mappings."""
        if not v:
            return v
        
        # Validate pin names and functions
        for pin_name, pin_function in v.items():
            if not pin_name.strip() or not pin_function.strip():
                raise ValueError("Pin names and functions cannot be empty")
            
            # Pin names should be alphanumeric with optional numbers
            if not pin_name.replace("_", "").replace("-", "").isalnum():
                raise ValueError(f"Invalid pin name: {pin_name}")
        
        return v
    
    @field_validator("electrical_specs")
    @classmethod
    def validate_electrical_specs(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate electrical specifications."""
        if not v:
            return v
        
        # Validate common electrical parameters
        if "supply_voltage_min" in v and "supply_voltage_max" in v:
            v_min = v["supply_voltage_min"]
            v_max = v["supply_voltage_max"]
            
            if not isinstance(v_min, (int, float)) or not isinstance(v_max, (int, float)):
                raise ValueError("Supply voltages must be numeric")
            
            if v_min >= v_max:
                raise ValueError("Minimum supply voltage must be less than maximum")
            
            if v_min < 0 or v_max > 50:
                raise ValueError("Supply voltages must be between 0 and 50V")
        
        if "current_consumption" in v:
            current = v["current_consumption"]
            if not isinstance(current, (int, float)) or current < 0:
                raise ValueError("Current consumption must be non-negative")
        
        return v
    
    @model_validator(mode="after")
    def validate_component_consistency(self) -> "Component":
        """Validate component data consistency."""
        # Ensure microcontrollers have GPIO pins
        if self.category == "microcontroller" and not any("GPIO" in pin or "IO" in pin for pin in self.pins.values()):
            raise ValueError("Microcontrollers must have GPIO pins defined")
        
        # Ensure power components have voltage specifications
        if self.category == "power" and "supply_voltage_min" not in self.electrical_specs:
            raise ValueError("Power components must have voltage specifications")
        
        return self


class SchematicResult(BaseModel):
    """Generated schematic with validation results."""
    
    svg_preview: str = Field(..., min_length=1)
    kicad_sexpr: str = Field(..., min_length=1)
    netlist: str = Field(..., min_length=1)
    warnings: List[str] = Field(default_factory=list)
    bom: List[Component] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator("svg_preview")
    @classmethod
    def validate_svg_preview(cls, v: str) -> str:
        """Validate SVG content is safe."""
        if not v.strip():
            raise ValueError("SVG preview cannot be empty")
        
        # Basic SVG validation - must start with SVG tag
        if not v.strip().startswith("<svg"):
            raise ValueError("Invalid SVG format")
        
        # Security check - no script tags allowed
        if "<script" in v.lower():
            raise ValueError("SVG cannot contain script tags")
        
        return v
    
    @field_validator("kicad_sexpr")
    @classmethod
    def validate_kicad_sexpr(cls, v: str) -> str:
        """Validate KiCad S-expression format."""
        if not v.strip():
            raise ValueError("KiCad S-expression cannot be empty")
        
        # Basic validation - should start with kicad_sch
        if not v.strip().startswith("(kicad_sch"):
            raise ValueError("Invalid KiCad S-expression format")
        
        return v
    
    @field_validator("warnings")
    @classmethod
    def validate_warnings(cls, v: List[str]) -> List[str]:
        """Validate warning messages."""
        # Filter out empty warnings and limit length
        filtered_warnings = []
        for warning in v:
            if warning.strip() and len(warning) <= 500:
                filtered_warnings.append(warning.strip())
        
        return filtered_warnings[:10]  # Limit to 10 warnings max


class Project(BaseModel):
    """Complete project with all associated data."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    prompt: ParsedPrompt
    shortlist: Dict[str, List[Component]] = Field(
        default_factory=dict,
        description="Component shortlists by role"
    )
    selections: Dict[str, str] = Field(
        default_factory=dict,
        description="Selected component MPNs by role"
    )
    schematic: Optional[SchematicResult] = None
    status: ProjectStatus = Field(default=ProjectStatus.CREATED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name."""
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        
        # Allow alphanumeric, spaces, hyphens, underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Project name contains invalid characters")
        
        return v.strip()
    
    @field_validator("selections")
    @classmethod
    def validate_selections(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate component selections."""
        for role, mpn in v.items():
            if not role.strip() or not mpn.strip():
                raise ValueError("Role and MPN cannot be empty")
        
        return v
    
    @model_validator(mode="after")
    def validate_project_consistency(self) -> "Project":
        """Validate project data consistency."""
        # Ensure selections match shortlist roles
        for role in self.selections.keys():
            if role not in self.shortlist:
                raise ValueError(f"Selection for role '{role}' not in shortlist")
        
        # Update timestamp
        self.updated_at = datetime.now(timezone.utc)
        
        return self
    
    def get_selected_components(self) -> List[Component]:
        """Get list of selected components."""
        selected = []
        for role, mpn in self.selections.items():
            if role in self.shortlist:
                for component in self.shortlist[role]:
                    if component.mpn == mpn:
                        selected.append(component)
                        break
        return selected
    
    def is_ready_for_generation(self) -> bool:
        """Check if project has all required selections for generation."""
        # Must have at least one selection
        if not self.selections:
            return False
        
        # All selections must have corresponding components in shortlist
        for role, mpn in self.selections.items():
            if role not in self.shortlist:
                return False
            
            component_found = any(comp.mpn == mpn for comp in self.shortlist[role])
            if not component_found:
                return False
        
        return True