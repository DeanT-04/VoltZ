"""Unit tests for PlannerService."""

import pytest
from typing import Dict, Any

from backend.src.services.planner import PlannerService
from backend.src.models.core import ParsedPrompt


class TestPlannerService:
    """Test cases for PlannerService prompt parsing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = PlannerService()
    
    def test_parse_prompt_empty_input(self):
        """Test that empty prompts raise ValueError."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.planner.parse_prompt("")
        
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.planner.parse_prompt("   ")
    
    def test_extract_roles_basic_microcontroller(self):
        """Test extraction of microcontroller role."""
        prompt = "I need an ESP32 microcontroller for my project"
        roles = self.planner.extract_roles(prompt)
        
        assert "microcontroller" in roles
        assert roles["microcontroller"] == "esp32"
    
    def test_extract_roles_basic_sensor(self):
        """Test extraction of sensor role."""
        prompt = "Add a temperature sensor to measure ambient temperature"
        roles = self.planner.extract_roles(prompt)
        
        assert "sensor" in roles
        assert roles["sensor"] == "temperature"
    
    def test_extract_roles_basic_power(self):
        """Test extraction of power role."""
        prompt = "Need a battery power supply for portable operation"
        roles = self.planner.extract_roles(prompt)
        
        assert "power" in roles
        assert roles["power"] == "battery"
    
    def test_extract_constraints_voltage_max(self):
        """Test extraction of maximum voltage constraint."""
        prompt = "Circuit should work with maximum 5V supply"
        constraints = self.planner.extract_constraints(prompt)
        
        assert "max_voltage" in constraints
        assert constraints["max_voltage"] == 5.0
    
    def test_extract_constraints_voltage_min(self):
        """Test extraction of minimum voltage constraint."""
        prompt = "Needs at least 3.3V to operate properly"
        constraints = self.planner.extract_constraints(prompt)
        
        assert "min_voltage" in constraints
        assert constraints["min_voltage"] == 3.3
    
    def test_extract_constraints_size(self):
        """Test extraction of size constraints."""
        prompt = "Make it small and compact for wearable use"
        constraints = self.planner.extract_constraints(prompt)
        
        assert "max_size" in constraints
        assert constraints["max_size"] == "small"
    
    def test_extract_constraints_battery_type(self):
        """Test extraction of battery type constraints."""
        prompt = "Use a LiPo battery for long runtime"
        constraints = self.planner.extract_constraints(prompt)
        
        assert "battery_type" in constraints
        assert constraints["battery_type"] == "lipo"
    
    def test_extract_constraints_current(self):
        """Test extraction of current constraints."""
        prompt = "Keep power consumption under 100mA maximum"
        constraints = self.planner.extract_constraints(prompt)
        
        assert "max_current_ma" in constraints
        assert constraints["max_current_ma"] == 100.0
    
    # 12 comprehensive test prompts for 90% accuracy target
    
    def test_prompt_1_iot_temperature_monitor(self):
        """Test Prompt 1: IoT temperature monitoring system."""
        prompt = "Build an IoT temperature monitoring system with ESP32 and DS18B20 sensor, powered by LiPo battery, max 3.3V"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "sensor" in result.roles
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("max_voltage") == 3.3
        assert result.constraints.get("battery_type") == "lipo"
        
        # Verify project name generation
        assert "Temperature" in result.project_name or "IoT" in result.project_name
    
    def test_prompt_2_home_automation_controller(self):
        """Test Prompt 2: Home automation controller with relays."""
        prompt = "Create a home automation controller using Arduino with relay modules to control lights, 5V power supply"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "actuator" in result.roles  # relay should be classified as actuator
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("target_voltage") == 5.0
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_3_wireless_sensor_network(self):
        """Test Prompt 3: Wireless sensor network node."""
        prompt = "Design a wireless sensor node with STM32, BME280 humidity sensor, and LoRa communication, small form factor"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "sensor" in result.roles
        assert "communication" in result.roles
        assert "power" in result.roles  # Should be inferred
        
        # Verify constraints extraction
        assert result.constraints.get("max_size") == "small"
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_4_motor_control_system(self):
        """Test Prompt 4: Motor control system with feedback."""
        prompt = "Build a stepper motor controller with encoder feedback using PIC microcontroller, 12V supply, maximum 2A current"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "actuator" in result.roles  # stepper motor
        assert "sensor" in result.roles or "analog" in result.roles  # encoder feedback
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("target_voltage") == 12.0
        assert result.constraints.get("max_current_a") == 2.0
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_5_data_logger_system(self):
        """Test Prompt 5: Data logging system with storage."""
        prompt = "Create a data logger for pressure and temperature with SD card storage, ESP8266 WiFi, coin battery"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "sensor" in result.roles
        assert "memory" in result.roles  # SD card storage
        assert "communication" in result.roles  # WiFi
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("battery_type") == "coin"
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_6_display_controller(self):
        """Test Prompt 6: Display controller with user interface."""
        prompt = "Design an OLED display controller with rotary encoder input, Arduino Nano, 5V max, compact size"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "display" in result.roles
        assert "sensor" in result.roles or "analog" in result.roles  # rotary encoder
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("max_voltage") == 5.0
        assert result.constraints.get("max_size") == "small"  # compact
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_7_power_monitoring_device(self):
        """Test Prompt 7: Power monitoring device with current sensing."""
        prompt = "Build a power monitor with INA219 current sensor and ESP32, measure up to 10A, Li-ion battery"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles
        assert "sensor" in result.roles or "analog" in result.roles  # current sensor
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("battery_type") == "li-ion"
        
        # Verify project name
        assert "Monitor" in result.project_name or "Power" in result.project_name
    
    def test_prompt_8_environmental_station(self):
        """Test Prompt 8: Environmental monitoring station."""
        prompt = "Environmental monitoring station with multiple sensors: temperature, humidity, air quality, solar powered"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles  # Should be inferred
        assert "sensor" in result.roles
        assert "power" in result.roles
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_9_alarm_system(self):
        """Test Prompt 9: Security alarm system with multiple components."""
        prompt = "Security alarm with PIR motion sensor, buzzer, LED indicators, GSM communication, 12V backup battery"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles  # Should be inferred
        assert "sensor" in result.roles  # PIR
        assert "actuator" in result.roles  # buzzer, LED
        assert "communication" in result.roles  # GSM
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("target_voltage") == 12.0
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_10_robotics_controller(self):
        """Test Prompt 10: Robotics controller with multiple actuators."""
        prompt = "Robot controller with servo motors, ultrasonic distance sensor, Bluetooth control, minimum 6V operation"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles  # Should be inferred
        assert "actuator" in result.roles  # servo motors
        assert "sensor" in result.roles  # ultrasonic
        assert "communication" in result.roles  # Bluetooth
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("min_voltage") == 6.0
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_11_measurement_instrument(self):
        """Test Prompt 11: Precision measurement instrument."""
        prompt = "Precision voltage measurement device with 16-bit ADC, LCD display, calibration memory, low power design"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles  # Should be inferred
        assert "analog" in result.roles  # ADC
        assert "display" in result.roles  # LCD
        assert "memory" in result.roles  # calibration storage
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("low_power") == True
        
        # Verify project name
        assert len(result.project_name) > 0
    
    def test_prompt_12_industrial_controller(self):
        """Test Prompt 12: Industrial process controller."""
        prompt = "Industrial process controller with 4-20mA current loop inputs, relay outputs, Modbus RTU, 24V industrial supply"
        
        result = self.planner.parse_prompt(prompt)
        
        # Verify roles extraction
        assert "microcontroller" in result.roles  # Should be inferred
        assert "analog" in result.roles  # current loop
        assert "actuator" in result.roles  # relay outputs
        assert "communication" in result.roles  # Modbus
        assert "power" in result.roles
        
        # Verify constraints extraction
        assert result.constraints.get("target_voltage") == 24.0
        
        # Verify project name
        assert "Controller" in result.project_name or "Industrial" in result.project_name
    
    def test_role_inference_sensor_needs_mcu(self):
        """Test that sensors automatically infer need for microcontroller."""
        prompt = "Temperature sensor for data logging"
        roles = self.planner.extract_roles(prompt)
        
        # Should infer microcontroller need
        assert "sensor" in roles
        assert "microcontroller" in roles
    
    def test_role_inference_actuator_needs_mcu(self):
        """Test that actuators automatically infer need for microcontroller."""
        prompt = "Control relay to switch lights"
        roles = self.planner.extract_roles(prompt)
        
        # Should infer microcontroller need
        assert "actuator" in roles
        assert "microcontroller" in roles
    
    def test_role_inference_mcu_needs_power(self):
        """Test that microcontrollers automatically infer need for power."""
        prompt = "ESP32 for IoT application"
        roles = self.planner.extract_roles(prompt)
        
        # Should infer power need
        assert "microcontroller" in roles
        assert "power" in roles
    
    def test_constraint_validation_voltage_range(self):
        """Test voltage constraint validation."""
        # Valid voltage
        prompt = "5V power supply"
        constraints = self.planner.extract_constraints(prompt)
        assert constraints.get("target_voltage") == 5.0
        
        # Should ignore invalid voltages (too high)
        prompt = "100V power supply"
        constraints = self.planner.extract_constraints(prompt)
        assert "target_voltage" not in constraints
    
    def test_constraint_battery_capacity_extraction(self):
        """Test battery capacity constraint extraction."""
        prompt = "Use 2000mAh LiPo battery for long runtime"
        constraints = self.planner.extract_constraints(prompt)
        
        assert constraints.get("battery_type") == "lipo"
        assert constraints.get("battery_capacity_mah") == 2000
    
    def test_constraint_frequency_extraction(self):
        """Test frequency constraint extraction."""
        prompt = "Microcontroller running at 80MHz clock speed"
        constraints = self.planner.extract_constraints(prompt)
        
        assert constraints.get("frequency_mhz") == 80.0
    
    def test_project_name_extraction_explicit(self):
        """Test explicit project name extraction."""
        prompt = "Build a Weather Station project with temperature sensor"
        result = self.planner.parse_prompt(prompt)
        
        assert "Weather Station" in result.project_name
    
    def test_project_name_generation_from_components(self):
        """Test project name generation from components."""
        prompt = "Temperature sensor with wireless monitoring"
        result = self.planner.parse_prompt(prompt)
        
        # Should generate name from key components
        assert any(word in result.project_name for word in ["Temperature", "Sensor", "Wireless"])
    
    def test_clean_prompt_normalization(self):
        """Test prompt cleaning and normalization."""
        prompt = "Please help me build a temp sensor with MCU for pwr management"
        clean = self.planner._clean_prompt(prompt)
        
        # Should normalize abbreviations
        assert "temperature" in clean.lower()
        assert "microcontroller" in clean.lower()
        assert "power" in clean.lower()
        
        # Should remove filler words
        assert "please" not in clean.lower()
        assert "help" not in clean.lower()
    
    def test_multiple_voltage_constraints(self):
        """Test handling of multiple voltage constraints."""
        prompt = "Circuit needs minimum 3V and maximum 5V operation"
        constraints = self.planner.extract_constraints(prompt)
        
        assert constraints.get("min_voltage") == 3.0
        assert constraints.get("max_voltage") == 5.0
    
    def test_complex_multi_role_prompt(self):
        """Test complex prompt with multiple roles and constraints."""
        prompt = """
        Design a smart home energy monitor with ESP32 microcontroller, 
        current sensor for power measurement, OLED display for readings,
        WiFi connectivity, SD card data logging, powered by 5V adapter,
        compact form factor for wall mounting
        """
        
        result = self.planner.parse_prompt(prompt)
        
        # Should extract multiple roles
        expected_roles = ["microcontroller", "sensor", "display", "communication", "memory", "power"]
        found_roles = list(result.roles.keys())
        
        # Should find most expected roles (allow some flexibility)
        overlap = len(set(expected_roles) & set(found_roles))
        assert overlap >= 4, f"Expected at least 4 roles, found {overlap}: {found_roles}"
        
        # Should extract constraints
        assert result.constraints.get("target_voltage") == 5.0
        assert result.constraints.get("max_size") == "small"  # compact
        
        # Should generate meaningful project name
        assert len(result.project_name) > 5


def test_planner_accuracy_benchmark():
    """Benchmark test to verify 90% extraction accuracy across all test prompts."""
    planner = PlannerService()
    
    # Define expected results for accuracy calculation
    test_cases = [
        {
            "prompt": "Build an IoT temperature monitoring system with ESP32 and DS18B20 sensor, powered by LiPo battery, max 3.3V",
            "expected_roles": ["microcontroller", "sensor", "power"],
            "expected_constraints": ["max_voltage", "battery_type"]
        },
        {
            "prompt": "Create a home automation controller using Arduino with relay modules to control lights, 5V power supply",
            "expected_roles": ["microcontroller", "actuator", "power"],
            "expected_constraints": ["target_voltage"]
        },
        {
            "prompt": "Design a wireless sensor node with STM32, BME280 humidity sensor, and LoRa communication, small form factor",
            "expected_roles": ["microcontroller", "sensor", "communication", "power"],
            "expected_constraints": ["max_size"]
        },
        {
            "prompt": "Build a stepper motor controller with encoder feedback using PIC microcontroller, 12V supply, maximum 2A current",
            "expected_roles": ["microcontroller", "actuator", "power"],
            "expected_constraints": ["target_voltage", "max_current_a"]
        },
        {
            "prompt": "Create a data logger for pressure and temperature with SD card storage, ESP8266 WiFi, coin battery",
            "expected_roles": ["microcontroller", "sensor", "memory", "communication", "power"],
            "expected_constraints": ["battery_type"]
        }
    ]
    
    total_expected = 0
    total_found = 0
    
    for test_case in test_cases:
        result = planner.parse_prompt(test_case["prompt"])
        
        # Count role accuracy
        for expected_role in test_case["expected_roles"]:
            total_expected += 1
            if expected_role in result.roles:
                total_found += 1
        
        # Count constraint accuracy
        for expected_constraint in test_case["expected_constraints"]:
            total_expected += 1
            if expected_constraint in result.constraints:
                total_found += 1
    
    accuracy = (total_found / total_expected) * 100 if total_expected > 0 else 0
    
    print(f"Extraction accuracy: {accuracy:.1f}% ({total_found}/{total_expected})")
    
    # Should achieve at least 90% accuracy
    assert accuracy >= 90.0, f"Accuracy {accuracy:.1f}% is below 90% target"