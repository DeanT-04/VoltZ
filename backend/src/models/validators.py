"""Validation utilities for electrical specifications and pin mappings."""

import re
from typing import Any, Dict, List, Optional, Tuple


class ElectricalSpecValidator:
    """Validator for electrical specifications."""
    
    # Common electrical parameter patterns
    VOLTAGE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(V|mV)$", re.IGNORECASE)
    CURRENT_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(A|mA|µA|uA)$", re.IGNORECASE)
    FREQUENCY_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(Hz|kHz|MHz|GHz)$", re.IGNORECASE)
    POWER_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(W|mW|µW|uW)$", re.IGNORECASE)
    
    @classmethod
    def validate_voltage_range(cls, min_voltage: float, max_voltage: float) -> bool:
        """Validate voltage range is reasonable."""
        if min_voltage >= max_voltage:
            return False
        
        if min_voltage < 0 or max_voltage > 50:
            return False
        
        # Check for reasonable voltage ranges
        voltage_diff = max_voltage - min_voltage
        if voltage_diff > 30:  # Very wide range might be suspicious
            return False
        
        return True
    
    @classmethod
    def validate_current_consumption(cls, current: float, unit: str = "mA") -> bool:
        """Validate current consumption is reasonable."""
        if current < 0:
            return False
        
        # Convert to mA for comparison
        if unit.lower() == "a":
            current_ma = current * 1000
        elif unit.lower() in ["ua", "µa"]:
            current_ma = current / 1000
        else:  # mA
            current_ma = current
        
        # Reasonable range: 0.001mA to 10A (10000mA)
        return 0.001 <= current_ma <= 10000
    
    @classmethod
    def validate_frequency(cls, frequency: float, unit: str = "Hz") -> bool:
        """Validate frequency is reasonable."""
        if frequency <= 0:
            return False
        
        # Convert to Hz for comparison
        if unit.lower() == "khz":
            freq_hz = frequency * 1000
        elif unit.lower() == "mhz":
            freq_hz = frequency * 1000000
        elif unit.lower() == "ghz":
            freq_hz = frequency * 1000000000
        else:  # Hz
            freq_hz = frequency
        
        # Reasonable range: 1Hz to 10GHz
        return 1 <= freq_hz <= 10_000_000_000
    
    @classmethod
    def parse_voltage_string(cls, voltage_str: str) -> Optional[Tuple[float, str]]:
        """Parse voltage string and return value and unit."""
        match = cls.VOLTAGE_PATTERN.match(voltage_str.strip())
        if match:
            value = float(match.group(1))
            unit = match.group(2).upper()
            return value, unit
        return None
    
    @classmethod
    def parse_current_string(cls, current_str: str) -> Optional[Tuple[float, str]]:
        """Parse current string and return value and unit."""
        match = cls.CURRENT_PATTERN.match(current_str.strip())
        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return value, unit
        return None
    
    @classmethod
    def validate_electrical_specs(cls, specs: Dict[str, Any]) -> List[str]:
        """Validate electrical specifications and return list of errors."""
        errors = []
        
        # Validate supply voltage range
        if "supply_voltage_min" in specs and "supply_voltage_max" in specs:
            try:
                v_min = float(specs["supply_voltage_min"])
                v_max = float(specs["supply_voltage_max"])
                
                if not cls.validate_voltage_range(v_min, v_max):
                    errors.append("Invalid supply voltage range")
            except (ValueError, TypeError):
                errors.append("Supply voltage values must be numeric")
        
        # Validate current consumption
        if "current_consumption" in specs:
            try:
                current = float(specs["current_consumption"])
                unit = specs.get("current_unit", "mA")
                
                if not cls.validate_current_consumption(current, unit):
                    errors.append("Invalid current consumption value")
            except (ValueError, TypeError):
                errors.append("Current consumption must be numeric")
        
        # Validate operating frequency
        if "operating_frequency" in specs:
            try:
                freq = float(specs["operating_frequency"])
                unit = specs.get("frequency_unit", "Hz")
                
                if not cls.validate_frequency(freq, unit):
                    errors.append("Invalid operating frequency")
            except (ValueError, TypeError):
                errors.append("Operating frequency must be numeric")
        
        # Validate temperature range
        if "temp_min" in specs and "temp_max" in specs:
            try:
                temp_min = float(specs["temp_min"])
                temp_max = float(specs["temp_max"])
                
                if temp_min >= temp_max:
                    errors.append("Minimum temperature must be less than maximum")
                
                if temp_min < -273 or temp_max > 200:
                    errors.append("Temperature range outside reasonable limits")
            except (ValueError, TypeError):
                errors.append("Temperature values must be numeric")
        
        return errors


class PinMappingValidator:
    """Validator for component pin mappings."""
    
    # Common pin function patterns
    POWER_PINS = {"VCC", "VDD", "VIN", "V+", "VBAT", "3V3", "5V", "12V", "POWER"}
    GROUND_PINS = {"GND", "VSS", "V-", "AGND", "DGND", "PGND", "GROUND"}
    GPIO_PATTERNS = [
        re.compile(r"^GPIO\d+$", re.IGNORECASE),
        re.compile(r"^IO\d+$", re.IGNORECASE),
        re.compile(r"^P[A-Z]\d+$", re.IGNORECASE),  # PA0, PB1, etc.
        re.compile(r"^PIN\d+$", re.IGNORECASE),
    ]
    
    @classmethod
    def validate_pin_name(cls, pin_name: str) -> bool:
        """Validate pin name format."""
        if not pin_name or not pin_name.strip():
            return False
        
        # Allow alphanumeric with underscores, hyphens, and dots
        pattern = re.compile(r"^[A-Za-z0-9_\-\.]+$")
        return bool(pattern.match(pin_name.strip()))
    
    @classmethod
    def validate_pin_function(cls, pin_function: str) -> bool:
        """Validate pin function description."""
        if not pin_function or not pin_function.strip():
            return False
        
        # Allow alphanumeric, spaces, common symbols
        pattern = re.compile(r"^[A-Za-z0-9_\-\.\s\+\/\(\)]+$")
        return bool(pattern.match(pin_function.strip()))
    
    @classmethod
    def is_power_pin(cls, pin_function: str) -> bool:
        """Check if pin function indicates a power pin."""
        pin_upper = pin_function.upper()
        return any(power_pin in pin_upper for power_pin in cls.POWER_PINS)
    
    @classmethod
    def is_ground_pin(cls, pin_function: str) -> bool:
        """Check if pin function indicates a ground pin."""
        return any(ground_pin in pin_function.upper() for ground_pin in cls.GROUND_PINS)
    
    @classmethod
    def is_gpio_pin(cls, pin_function: str) -> bool:
        """Check if pin function indicates a GPIO pin."""
        pin_upper = pin_function.upper()
        
        # Check for explicit GPIO keywords
        if any(keyword in pin_upper for keyword in ["GPIO", "GENERAL PURPOSE", "IO"]):
            return True
        
        # Check for pattern matches
        return any(pattern.match(pin_function) for pattern in cls.GPIO_PATTERNS)
    
    @classmethod
    def validate_pin_mapping(cls, pins: Dict[str, str]) -> List[str]:
        """Validate complete pin mapping and return list of errors."""
        errors = []
        
        if not pins:
            return ["Pin mapping cannot be empty"]
        
        power_pins = []
        ground_pins = []
        gpio_pins = []
        
        for pin_name, pin_function in pins.items():
            # Validate individual pin name and function
            if not cls.validate_pin_name(pin_name):
                errors.append(f"Invalid pin name: {pin_name}")
            
            if not cls.validate_pin_function(pin_function):
                errors.append(f"Invalid pin function: {pin_function}")
            
            # Categorize pins
            if cls.is_power_pin(pin_function):
                power_pins.append(pin_name)
            elif cls.is_ground_pin(pin_function):
                ground_pins.append(pin_name)
            elif cls.is_gpio_pin(pin_function):
                gpio_pins.append(pin_name)
        
        # Validate pin requirements
        if not power_pins:
            errors.append("Component must have at least one power pin")
        
        if not ground_pins:
            errors.append("Component must have at least one ground pin")
        
        # Check for duplicate pin names
        pin_names = list(pins.keys())
        if len(pin_names) != len(set(pin_names)):
            errors.append("Duplicate pin names found")
        
        return errors
    
    @classmethod
    def validate_microcontroller_pins(cls, pins: Dict[str, str]) -> List[str]:
        """Validate microcontroller-specific pin requirements."""
        errors = cls.validate_pin_mapping(pins)
        
        # Microcontrollers need GPIO pins
        gpio_count = sum(1 for func in pins.values() if cls.is_gpio_pin(func))
        if gpio_count < 2:
            errors.append("Microcontroller must have at least 2 GPIO pins")
        
        return errors
    
    @classmethod
    def validate_sensor_pins(cls, pins: Dict[str, str]) -> List[str]:
        """Validate sensor-specific pin requirements."""
        errors = cls.validate_pin_mapping(pins)
        
        # Sensors typically need data/signal pins
        signal_pins = [name for name, func in pins.items() 
                      if any(signal in func.upper() for signal in ["DATA", "OUT", "SIGNAL", "SDA", "SCL"])]
        
        if not signal_pins:
            errors.append("Sensor must have at least one data/signal pin")
        
        return errors


def validate_component_electrical_compatibility(
    components: List[Dict[str, Any]]
) -> List[str]:
    """Validate electrical compatibility between components."""
    errors = []
    
    if len(components) < 2:
        return errors
    
    # Extract voltage requirements
    voltage_ranges = []
    for comp in components:
        specs = comp.get("electrical_specs", {})
        if "supply_voltage_min" in specs and "supply_voltage_max" in specs:
            v_min = specs["supply_voltage_min"]
            v_max = specs["supply_voltage_max"]
            voltage_ranges.append((v_min, v_max, comp.get("mpn", "Unknown")))
    
    # Check for voltage compatibility
    if len(voltage_ranges) > 1:
        # Find common voltage range
        common_min = max(v_range[0] for v_range in voltage_ranges)
        common_max = min(v_range[1] for v_range in voltage_ranges)
        
        if common_min >= common_max:
            incompatible_parts = [v_range[2] for v_range in voltage_ranges]
            errors.append(f"Voltage incompatibility between components: {', '.join(incompatible_parts)}")
    
    return errors