"""Tests for core data models."""

import pytest
from datetime import datetime
from uuid import UUID
from pydantic import ValidationError

from backend.src.models.core import (
    Component,
    ParsedPrompt,
    Project,
    ProjectStatus,
    SchematicResult,
)


class TestParsedPrompt:
    """Tests for ParsedPrompt model."""
    
    def test_valid_parsed_prompt(self):
        """Test creating a valid ParsedPrompt."""
        prompt = ParsedPrompt(
            project_name="Test Project",
            roles={"microcontroller": "ESP32", "sensor": "temperature"},
            constraints={"max_voltage": 3.3, "max_size": "small"}
        )
        
        assert prompt.project_name == "Test Project"
        assert prompt.roles["microcontroller"] == "ESP32"
        assert prompt.constraints["max_voltage"] == 3.3
    
    def test_project_name_validation(self):
        """Test project name validation."""
        # Valid names
        ParsedPrompt(project_name="Valid Name")
        ParsedPrompt(project_name="Valid-Name_123")
        
        # Invalid names - empty string triggers Pydantic's min_length validation
        with pytest.raises(ValidationError):
            ParsedPrompt(project_name="")
        
        # Invalid names - custom validation
        with pytest.raises(ValidationError, match="Project name cannot be empty"):
            ParsedPrompt(project_name="   ")
        
        with pytest.raises(ValidationError, match="contains invalid characters"):
            ParsedPrompt(project_name="Invalid@Name")
    
    def test_roles_validation(self):
        """Test roles validation."""
        # Valid roles
        ParsedPrompt(
            project_name="Test",
            roles={"microcontroller": "ESP32", "sensor": "temp"}
        )
        
        # Invalid role
        with pytest.raises(ValidationError, match="Invalid role"):
            ParsedPrompt(
                project_name="Test",
                roles={"invalid_role": "component"}
            )
    
    def test_constraints_validation(self):
        """Test constraints validation."""
        # Valid constraints
        ParsedPrompt(
            project_name="Test",
            constraints={
                "max_voltage": 5.0,
                "min_voltage": 1.8,
                "max_size": "medium"
            }
        )
        
        # Invalid voltage constraints
        with pytest.raises(ValidationError, match="max_voltage must be between"):
            ParsedPrompt(
                project_name="Test",
                constraints={"max_voltage": -1}
            )
        
        with pytest.raises(ValidationError, match="max_voltage must be between"):
            ParsedPrompt(
                project_name="Test",
                constraints={"max_voltage": 100}
            )
        
        # Invalid size constraint
        with pytest.raises(ValidationError, match="max_size must be"):
            ParsedPrompt(
                project_name="Test",
                constraints={"max_size": "huge"}
            )


class TestComponent:
    """Tests for Component model."""
    
    def test_valid_component(self):
        """Test creating a valid Component."""
        component = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi and Bluetooth microcontroller",
            category="microcontroller",
            pins={
                "GPIO0": "GPIO/Boot",
                "VCC": "Power Supply",
                "GND": "Ground"
            },
            electrical_specs={
                "supply_voltage_min": 2.7,
                "supply_voltage_max": 3.6,
                "current_consumption": 80
            }
        )
        
        assert component.mpn == "ESP32-WROOM-32"
        assert component.manufacturer == "Espressif"
        assert component.category == "microcontroller"
    
    def test_mpn_validation(self):
        """Test MPN validation."""
        # Valid MPNs - need GPIO pins for microcontroller
        Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="Test",
            category="microcontroller",
            pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
        )
        
        # Invalid MPNs - empty string triggers Pydantic's min_length validation
        with pytest.raises(ValidationError):
            Component(
                mpn="",
                manufacturer="Test",
                description="Test",
                category="test"
            )
        
        with pytest.raises(ValidationError, match="MPN contains invalid characters"):
            Component(
                mpn="ESP32@WROOM",
                manufacturer="Test",
                description="Test",
                category="test"
            )
    
    def test_pins_validation(self):
        """Test pin mapping validation."""
        # Valid pins
        Component(
            mpn="TEST-001",
            manufacturer="Test",
            description="Test",
            category="test",
            pins={"GPIO0": "General Purpose IO", "VCC": "Power"}
        )
        
        # Invalid pin names
        with pytest.raises(ValidationError, match="Invalid pin name"):
            Component(
                mpn="TEST-001",
                manufacturer="Test",
                description="Test",
                category="test",
                pins={"GPIO@0": "Invalid pin"}
            )
    
    def test_electrical_specs_validation(self):
        """Test electrical specifications validation."""
        # Valid specs
        Component(
            mpn="TEST-001",
            manufacturer="Test",
            description="Test",
            category="test",
            electrical_specs={
                "supply_voltage_min": 2.7,
                "supply_voltage_max": 3.6,
                "current_consumption": 50
            }
        )
        
        # Invalid voltage range
        with pytest.raises(ValidationError, match="Minimum supply voltage must be less"):
            Component(
                mpn="TEST-001",
                manufacturer="Test",
                description="Test",
                category="test",
                electrical_specs={
                    "supply_voltage_min": 5.0,
                    "supply_voltage_max": 3.3
                }
            )
        
        # Invalid current consumption
        with pytest.raises(ValidationError, match="Current consumption must be non-negative"):
            Component(
                mpn="TEST-001",
                manufacturer="Test",
                description="Test",
                category="test",
                electrical_specs={"current_consumption": -10}
            )
    
    def test_microcontroller_validation(self):
        """Test microcontroller-specific validation."""
        # Valid microcontroller with GPIO pins
        Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi microcontroller",
            category="microcontroller",
            pins={
                "GPIO0": "General Purpose IO",
                "GPIO1": "General Purpose IO",
                "VCC": "Power",
                "GND": "Ground"
            }
        )
        
        # Invalid microcontroller without GPIO pins
        with pytest.raises(ValidationError, match="Microcontrollers must have GPIO pins"):
            Component(
                mpn="ESP32-WROOM-32",
                manufacturer="Espressif",
                description="WiFi microcontroller",
                category="microcontroller",
                pins={"VCC": "Power", "GND": "Ground"}
            )
    
    def test_power_component_validation(self):
        """Test power component validation."""
        # Valid power component
        Component(
            mpn="LM7805",
            manufacturer="Texas Instruments",
            description="5V Linear Regulator",
            category="power",
            electrical_specs={
                "supply_voltage_min": 7.0,
                "supply_voltage_max": 35.0
            }
        )
        
        # Invalid power component without voltage specs
        with pytest.raises(ValidationError, match="Power components must have voltage specifications"):
            Component(
                mpn="LM7805",
                manufacturer="Texas Instruments",
                description="5V Linear Regulator",
                category="power"
            )


class TestSchematicResult:
    """Tests for SchematicResult model."""
    
    def test_valid_schematic_result(self):
        """Test creating a valid SchematicResult."""
        result = SchematicResult(
            svg_preview="<svg><rect/></svg>",
            kicad_sexpr="(kicad_sch (version 20230121))",
            netlist="(export (version D))",
            warnings=["Missing decoupling capacitor"],
            bom=[
                Component(
                    mpn="ESP32-WROOM-32",
                    manufacturer="Espressif",
                    description="WiFi microcontroller",
                    category="microcontroller",
                    pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
                )
            ]
        )
        
        assert "<svg>" in result.svg_preview
        assert result.kicad_sexpr.startswith("(kicad_sch")
        assert len(result.warnings) == 1
        assert len(result.bom) == 1
        assert isinstance(result.generated_at, datetime)
    
    def test_svg_validation(self):
        """Test SVG preview validation."""
        # Valid SVG
        SchematicResult(
            svg_preview="<svg><rect/></svg>",
            kicad_sexpr="(kicad_sch (version 20230121))",
            netlist="(export (version D))"
        )
        
        # Invalid SVG - empty (triggers Pydantic's min_length validation)
        with pytest.raises(ValidationError):
            SchematicResult(
                svg_preview="",
                kicad_sexpr="(kicad_sch (version 20230121))",
                netlist="(export (version D))"
            )
        
        # Invalid SVG - not SVG format
        with pytest.raises(ValidationError, match="Invalid SVG format"):
            SchematicResult(
                svg_preview="<div>Not SVG</div>",
                kicad_sexpr="(kicad_sch (version 20230121))",
                netlist="(export (version D))"
            )
        
        # Invalid SVG - contains script
        with pytest.raises(ValidationError, match="SVG cannot contain script tags"):
            SchematicResult(
                svg_preview="<svg><script>alert('xss')</script></svg>",
                kicad_sexpr="(kicad_sch (version 20230121))",
                netlist="(export (version D))"
            )
    
    def test_kicad_sexpr_validation(self):
        """Test KiCad S-expression validation."""
        # Valid KiCad S-expression
        SchematicResult(
            svg_preview="<svg><rect/></svg>",
            kicad_sexpr="(kicad_sch (version 20230121))",
            netlist="(export (version D))"
        )
        
        # Invalid - empty (triggers Pydantic's min_length validation)
        with pytest.raises(ValidationError):
            SchematicResult(
                svg_preview="<svg><rect/></svg>",
                kicad_sexpr="",
                netlist="(export (version D))"
            )
        
        # Invalid - wrong format
        with pytest.raises(ValidationError, match="Invalid KiCad S-expression format"):
            SchematicResult(
                svg_preview="<svg><rect/></svg>",
                kicad_sexpr="invalid format",
                netlist="(export (version D))"
            )
    
    def test_warnings_validation(self):
        """Test warnings validation."""
        # Valid warnings
        result = SchematicResult(
            svg_preview="<svg><rect/></svg>",
            kicad_sexpr="(kicad_sch (version 20230121))",
            netlist="(export (version D))",
            warnings=["Warning 1", "Warning 2", ""]  # Empty warning should be filtered
        )
        
        assert len(result.warnings) == 2
        assert "" not in result.warnings
        
        # Too many warnings - should be limited to 10
        long_warnings = [f"Warning {i}" for i in range(15)]
        result = SchematicResult(
            svg_preview="<svg><rect/></svg>",
            kicad_sexpr="(kicad_sch (version 20230121))",
            netlist="(export (version D))",
            warnings=long_warnings
        )
        
        assert len(result.warnings) == 10


class TestProject:
    """Tests for Project model."""
    
    def test_valid_project(self):
        """Test creating a valid Project."""
        prompt = ParsedPrompt(
            project_name="Test Project",
            roles={"microcontroller": "ESP32"},
            constraints={"max_voltage": 3.3}
        )
        
        project = Project(
            name="Test Project",
            prompt=prompt
        )
        
        assert isinstance(project.id, UUID)
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.CREATED
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
    
    def test_project_name_validation(self):
        """Test project name validation."""
        prompt = ParsedPrompt(project_name="Test")
        
        # Valid name
        Project(name="Valid Project Name", prompt=prompt)
        
        # Invalid name - empty string triggers Pydantic's min_length validation
        with pytest.raises(ValidationError):
            Project(name="", prompt=prompt)
        
        with pytest.raises(ValidationError, match="contains invalid characters"):
            Project(name="Invalid@Name", prompt=prompt)
    
    def test_selections_validation(self):
        """Test selections validation."""
        prompt = ParsedPrompt(project_name="Test")
        component = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi microcontroller",
            category="microcontroller",
            pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
        )
        
        # Valid selections
        Project(
            name="Test",
            prompt=prompt,
            shortlist={"microcontroller": [component]},
            selections={"microcontroller": "ESP32-WROOM-32"}
        )
        
        # Invalid selections - empty values
        with pytest.raises(ValidationError, match="Role and MPN cannot be empty"):
            Project(
                name="Test",
                prompt=prompt,
                shortlist={"microcontroller": [component]},
                selections={"microcontroller": ""}
            )
    
    def test_project_consistency_validation(self):
        """Test project consistency validation."""
        prompt = ParsedPrompt(project_name="Test")
        component = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi microcontroller",
            category="microcontroller",
            pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
        )
        
        # Valid project with matching shortlist and selections
        project = Project(
            name="Test",
            prompt=prompt,
            shortlist={"microcontroller": [component]},
            selections={"microcontroller": "ESP32-WROOM-32"}
        )
        
        # Should pass validation
        assert project.name == "Test"
        
        # Invalid project - selection not in shortlist
        with pytest.raises(ValidationError, match="Selection for role .* not in shortlist"):
            Project(
                name="Test",
                prompt=prompt,
                shortlist={"microcontroller": [component]},
                selections={"sensor": "TMP117"}  # Role not in shortlist
            )
    
    def test_get_selected_components(self):
        """Test getting selected components."""
        prompt = ParsedPrompt(project_name="Test")
        esp32 = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi microcontroller",
            category="microcontroller",
            pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
        )
        tmp117 = Component(
            mpn="TMP117",
            manufacturer="Texas Instruments",
            description="Temperature sensor",
            category="sensor",
            pins={"DATA": "Data Output", "VCC": "Power", "GND": "Ground"}
        )
        
        project = Project(
            name="Test",
            prompt=prompt,
            shortlist={
                "microcontroller": [esp32],
                "sensor": [tmp117]
            },
            selections={
                "microcontroller": "ESP32-WROOM-32",
                "sensor": "TMP117"
            }
        )
        
        selected = project.get_selected_components()
        assert len(selected) == 2
        assert esp32 in selected
        assert tmp117 in selected
    
    def test_is_ready_for_generation(self):
        """Test checking if project is ready for generation."""
        prompt = ParsedPrompt(project_name="Test")
        component = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi microcontroller",
            category="microcontroller",
            pins={"GPIO0": "GPIO", "VCC": "Power", "GND": "Ground"}
        )
        
        # Project without selections - not ready
        project = Project(name="Test", prompt=prompt)
        assert not project.is_ready_for_generation()
        
        # Project with valid selections - ready
        project = Project(
            name="Test",
            prompt=prompt,
            shortlist={"microcontroller": [component]},
            selections={"microcontroller": "ESP32-WROOM-32"}
        )
        assert project.is_ready_for_generation()
        
        # Project with invalid selections - not ready
        project = Project(
            name="Test",
            prompt=prompt,
            shortlist={"microcontroller": [component]},
            selections={"microcontroller": "INVALID-MPN"}
        )
        assert not project.is_ready_for_generation()


class TestModelSerialization:
    """Tests for model serialization and deserialization."""
    
    def test_component_serialization(self):
        """Test Component JSON serialization."""
        component = Component(
            mpn="ESP32-WROOM-32",
            manufacturer="Espressif",
            description="WiFi and Bluetooth microcontroller",
            category="microcontroller",
            pins={"GPIO0": "GPIO/Boot", "VCC": "Power"},
            electrical_specs={"supply_voltage_min": 2.7, "supply_voltage_max": 3.6}
        )
        
        # Test serialization
        json_data = component.model_dump()
        assert json_data["mpn"] == "ESP32-WROOM-32"
        assert json_data["manufacturer"] == "Espressif"
        
        # Test deserialization
        component_copy = Component.model_validate(json_data)
        assert component_copy.mpn == component.mpn
        assert component_copy.manufacturer == component.manufacturer
    
    def test_project_serialization(self):
        """Test Project JSON serialization."""
        prompt = ParsedPrompt(
            project_name="Test Project",
            roles={"microcontroller": "ESP32"},
            constraints={"max_voltage": 3.3}
        )
        
        project = Project(name="Test Project", prompt=prompt)
        
        # Test serialization
        json_data = project.model_dump()
        assert json_data["name"] == "Test Project"
        assert json_data["status"] == "created"
        
        # Test deserialization
        project_copy = Project.model_validate(json_data)
        assert project_copy.name == project.name
        assert project_copy.status == project.status