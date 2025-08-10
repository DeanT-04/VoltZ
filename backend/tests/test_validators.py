"""Tests for validation utilities."""

import pytest

from backend.src.models.validators import (
    ElectricalSpecValidator,
    PinMappingValidator,
    validate_component_electrical_compatibility,
)


class TestElectricalSpecValidator:
    """Tests for ElectricalSpecValidator."""
    
    def test_validate_voltage_range(self):
        """Test voltage range validation."""
        # Valid ranges
        assert ElectricalSpecValidator.validate_voltage_range(2.7, 3.6)
        assert ElectricalSpecValidator.validate_voltage_range(0.1, 5.0)
        
        # Invalid ranges
        assert not ElectricalSpecValidator.validate_voltage_range(3.6, 2.7)  # min > max
        assert not ElectricalSpecValidator.validate_voltage_range(-1, 3.3)   # negative min
        assert not ElectricalSpecValidator.validate_voltage_range(0, 100)    # max too high
        assert not ElectricalSpecValidator.validate_voltage_range(0, 35)     # range too wide
    
    def test_validate_current_consumption(self):
        """Test current consumption validation."""
        # Valid currents
        assert ElectricalSpecValidator.validate_current_consumption(50, "mA")
        assert ElectricalSpecValidator.validate_current_consumption(0.05, "A")
        assert ElectricalSpecValidator.validate_current_consumption(50000, "µA")
        
        # Invalid currents
        assert not ElectricalSpecValidator.validate_current_consumption(-10, "mA")  # negative
        assert not ElectricalSpecValidator.validate_current_consumption(20, "A")   # too high
        assert not ElectricalSpecValidator.validate_current_consumption(0.0001, "µA")  # too low
    
    def test_validate_frequency(self):
        """Test frequency validation."""
        # Valid frequencies
        assert ElectricalSpecValidator.validate_frequency(1000, "Hz")
        assert ElectricalSpecValidator.validate_frequency(16, "MHz")
        assert ElectricalSpecValidator.validate_frequency(2.4, "GHz")
        
        # Invalid frequencies
        assert not ElectricalSpecValidator.validate_frequency(0, "Hz")      # zero
        assert not ElectricalSpecValidator.validate_frequency(-100, "kHz")  # negative
        assert not ElectricalSpecValidator.validate_frequency(20, "GHz")    # too high
    
    def test_parse_voltage_string(self):
        """Test voltage string parsing."""
        # Valid voltage strings
        result = ElectricalSpecValidator.parse_voltage_string("3.3V")
        assert result == (3.3, "V")
        
        result = ElectricalSpecValidator.parse_voltage_string("1800mV")
        assert result == (1800.0, "MV")
        
        result = ElectricalSpecValidator.parse_voltage_string("5.0 V")
        assert result == (5.0, "V")
        
        # Invalid voltage strings
        assert ElectricalSpecValidator.parse_voltage_string("invalid") is None
        assert ElectricalSpecValidator.parse_voltage_string("3.3A") is None
    
    def test_parse_current_string(self):
        """Test current string parsing."""
        # Valid current strings
        result = ElectricalSpecValidator.parse_current_string("50mA")
        assert result == (50.0, "mA")
        
        result = ElectricalSpecValidator.parse_current_string("0.1A")
        assert result == (0.1, "A")
        
        result = ElectricalSpecValidator.parse_current_string("1000µA")
        assert result == (1000.0, "µA")
        
        # Invalid current strings
        assert ElectricalSpecValidator.parse_current_string("invalid") is None
        assert ElectricalSpecValidator.parse_current_string("50V") is None
    
    def test_validate_electrical_specs(self):
        """Test complete electrical specifications validation."""
        # Valid specs
        specs = {
            "supply_voltage_min": 2.7,
            "supply_voltage_max": 3.6,
            "current_consumption": 50,
            "current_unit": "mA",
            "operating_frequency": 16,
            "frequency_unit": "MHz",
            "temp_min": -40,
            "temp_max": 85
        }
        
        errors = ElectricalSpecValidator.validate_electrical_specs(specs)
        assert len(errors) == 0
        
        # Invalid voltage range
        specs["supply_voltage_min"] = 5.0
        specs["supply_voltage_max"] = 3.3
        errors = ElectricalSpecValidator.validate_electrical_specs(specs)
        assert any("voltage range" in error for error in errors)
        
        # Invalid current
        specs["supply_voltage_min"] = 2.7
        specs["supply_voltage_max"] = 3.6
        specs["current_consumption"] = -10
        errors = ElectricalSpecValidator.validate_electrical_specs(specs)
        assert any("current consumption" in error for error in errors)
        
        # Invalid temperature range
        specs["current_consumption"] = 50
        specs["temp_min"] = 100
        specs["temp_max"] = -40
        errors = ElectricalSpecValidator.validate_electrical_specs(specs)
        assert any("temperature" in error for error in errors)


class TestPinMappingValidator:
    """Tests for PinMappingValidator."""
    
    def test_validate_pin_name(self):
        """Test pin name validation."""
        # Valid pin names
        assert PinMappingValidator.validate_pin_name("GPIO0")
        assert PinMappingValidator.validate_pin_name("VCC")
        assert PinMappingValidator.validate_pin_name("PA0")
        assert PinMappingValidator.validate_pin_name("PIN_1")
        assert PinMappingValidator.validate_pin_name("ADC-IN")
        
        # Invalid pin names
        assert not PinMappingValidator.validate_pin_name("")
        assert not PinMappingValidator.validate_pin_name("   ")
        assert not PinMappingValidator.validate_pin_name("GPIO@0")
        assert not PinMappingValidator.validate_pin_name("PIN 1")  # space not allowed
    
    def test_validate_pin_function(self):
        """Test pin function validation."""
        # Valid pin functions
        assert PinMappingValidator.validate_pin_function("General Purpose IO")
        assert PinMappingValidator.validate_pin_function("Power Supply")
        assert PinMappingValidator.validate_pin_function("ADC Input (0-3.3V)")
        assert PinMappingValidator.validate_pin_function("UART_TX")
        
        # Invalid pin functions
        assert not PinMappingValidator.validate_pin_function("")
        assert not PinMappingValidator.validate_pin_function("   ")
        assert not PinMappingValidator.validate_pin_function("Invalid@Function")
    
    def test_is_power_pin(self):
        """Test power pin detection."""
        assert PinMappingValidator.is_power_pin("VCC")
        assert PinMappingValidator.is_power_pin("VDD Supply")
        assert PinMappingValidator.is_power_pin("3V3 Power")
        assert PinMappingValidator.is_power_pin("VBAT Input")
        
        assert not PinMappingValidator.is_power_pin("GPIO0")
        assert not PinMappingValidator.is_power_pin("Data Output")
    
    def test_is_ground_pin(self):
        """Test ground pin detection."""
        assert PinMappingValidator.is_ground_pin("GND")
        assert PinMappingValidator.is_ground_pin("VSS Ground")
        assert PinMappingValidator.is_ground_pin("AGND Analog Ground")
        assert PinMappingValidator.is_ground_pin("DGND Digital Ground")
        
        assert not PinMappingValidator.is_ground_pin("GPIO0")
        assert not PinMappingValidator.is_ground_pin("VCC")
    
    def test_is_gpio_pin(self):
        """Test GPIO pin detection."""
        assert PinMappingValidator.is_gpio_pin("GPIO0")
        assert PinMappingValidator.is_gpio_pin("gpio15")
        assert PinMappingValidator.is_gpio_pin("IO2")
        assert PinMappingValidator.is_gpio_pin("PA0")
        assert PinMappingValidator.is_gpio_pin("PIN1")
        
        assert not PinMappingValidator.is_gpio_pin("VCC")
        assert not PinMappingValidator.is_gpio_pin("UART_TX")
    
    def test_validate_pin_mapping(self):
        """Test complete pin mapping validation."""
        # Valid pin mapping
        pins = {
            "GPIO0": "General Purpose IO",
            "GPIO1": "General Purpose IO",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        
        errors = PinMappingValidator.validate_pin_mapping(pins)
        assert len(errors) == 0
        
        # Empty pin mapping
        errors = PinMappingValidator.validate_pin_mapping({})
        assert any("cannot be empty" in error for error in errors)
        
        # Missing power pin
        pins_no_power = {
            "GPIO0": "General Purpose IO",
            "GND": "Ground"
        }
        errors = PinMappingValidator.validate_pin_mapping(pins_no_power)
        assert any("power pin" in error for error in errors)
        
        # Missing ground pin
        pins_no_ground = {
            "GPIO0": "General Purpose IO",
            "VCC": "Power Supply"
        }
        errors = PinMappingValidator.validate_pin_mapping(pins_no_ground)
        assert any("ground pin" in error for error in errors)
        
        # Duplicate pin names
        pins_duplicate = {
            "GPIO0": "General Purpose IO",
            "GPIO0": "Duplicate Pin",  # This will overwrite the first one in dict
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        # Note: Python dict will automatically handle duplicates, so this test
        # is more about the concept than actual duplicate detection
        
        # Invalid pin name
        pins_invalid = {
            "GPIO@0": "Invalid Pin Name",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        errors = PinMappingValidator.validate_pin_mapping(pins_invalid)
        assert any("Invalid pin name" in error for error in errors)
    
    def test_validate_microcontroller_pins(self):
        """Test microcontroller-specific pin validation."""
        # Valid microcontroller pins
        pins = {
            "GPIO0": "General Purpose IO",
            "GPIO1": "General Purpose IO",
            "GPIO2": "General Purpose IO",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        
        errors = PinMappingValidator.validate_microcontroller_pins(pins)
        assert len(errors) == 0
        
        # Insufficient GPIO pins
        pins_few_gpio = {
            "GPIO0": "General Purpose IO",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        errors = PinMappingValidator.validate_microcontroller_pins(pins_few_gpio)
        assert any("at least 2 GPIO pins" in error for error in errors)
    
    def test_validate_sensor_pins(self):
        """Test sensor-specific pin validation."""
        # Valid sensor pins
        pins = {
            "DATA": "Data Output",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        
        errors = PinMappingValidator.validate_sensor_pins(pins)
        assert len(errors) == 0
        
        # Valid I2C sensor pins
        pins_i2c = {
            "SDA": "I2C Data",
            "SCL": "I2C Clock",
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        errors = PinMappingValidator.validate_sensor_pins(pins_i2c)
        assert len(errors) == 0
        
        # Missing data/signal pins
        pins_no_signal = {
            "VCC": "Power Supply",
            "GND": "Ground"
        }
        errors = PinMappingValidator.validate_sensor_pins(pins_no_signal)
        assert any("data/signal pin" in error for error in errors)


class TestComponentCompatibility:
    """Tests for component electrical compatibility validation."""
    
    def test_compatible_components(self):
        """Test components with compatible voltage ranges."""
        components = [
            {
                "mpn": "ESP32-WROOM-32",
                "electrical_specs": {
                    "supply_voltage_min": 2.7,
                    "supply_voltage_max": 3.6
                }
            },
            {
                "mpn": "TMP117",
                "electrical_specs": {
                    "supply_voltage_min": 1.8,
                    "supply_voltage_max": 5.5
                }
            }
        ]
        
        errors = validate_component_electrical_compatibility(components)
        assert len(errors) == 0
    
    def test_incompatible_components(self):
        """Test components with incompatible voltage ranges."""
        components = [
            {
                "mpn": "ESP32-WROOM-32",
                "electrical_specs": {
                    "supply_voltage_min": 2.7,
                    "supply_voltage_max": 3.6
                }
            },
            {
                "mpn": "12V-SENSOR",
                "electrical_specs": {
                    "supply_voltage_min": 10.0,
                    "supply_voltage_max": 15.0
                }
            }
        ]
        
        errors = validate_component_electrical_compatibility(components)
        assert len(errors) > 0
        assert any("Voltage incompatibility" in error for error in errors)
    
    def test_single_component(self):
        """Test validation with single component."""
        components = [
            {
                "mpn": "ESP32-WROOM-32",
                "electrical_specs": {
                    "supply_voltage_min": 2.7,
                    "supply_voltage_max": 3.6
                }
            }
        ]
        
        errors = validate_component_electrical_compatibility(components)
        assert len(errors) == 0
    
    def test_components_without_voltage_specs(self):
        """Test components without voltage specifications."""
        components = [
            {"mpn": "COMPONENT-1"},
            {"mpn": "COMPONENT-2"}
        ]
        
        errors = validate_component_electrical_compatibility(components)
        assert len(errors) == 0