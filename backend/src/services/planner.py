"""Planner service for parsing user prompts and extracting component roles and constraints."""

import re
from typing import Any, Dict, List, Optional, Tuple

from ..models.core import ParsedPrompt


class PlannerService:
    """Service for parsing user prompts into structured component requirements."""
    
    def __init__(self):
        """Initialize the planner service with regex patterns."""
        # Component role patterns - ordered by specificity
        self.role_patterns = {
            "microcontroller": [
                r"\b(?:microcontroller|mcu|esp32|esp8266|arduino|atmega|stm32|pic|arm|cortex)\b",
                r"\b(?:processor|cpu|controller|brain)\b",
                r"\b(?:wifi|bluetooth|ble)\s+(?:module|chip|board)\b"
            ],
            "sensor": [
                r"\b(?:sensor|temperature|humidity|pressure|accelerometer|gyroscope|magnetometer)\b",
                r"\b(?:tmp\d+|ds18b20|bmp\d+|mpu\d+|lsm\d+|hdc\d+|sht\d+)\b",
                r"\b(?:measure|detect|sense|monitor)\s+(?:temperature|humidity|pressure|motion|light)\b",
                r"\b(?:thermometer|barometer|hygrometer|proximity|ultrasonic|pir)\b"
            ],
            "power": [
                r"\b(?:power|battery|regulator|ldo|buck|boost|charger)\b",
                r"\b(?:voltage|supply|vcc|vdd|3v3|5v|12v)\b",
                r"\b(?:lipo|li-ion|alkaline|nimh|coin|cell)\b",
                r"\b(?:amp|current|mah|wh|watts)\b"
            ],
            "actuator": [
                r"\b(?:motor|servo|stepper|relay|solenoid|valve)\b",
                r"\b(?:led|light|display|buzzer|speaker|pump)\b",
                r"\b(?:drive|control|actuate|move|rotate)\b"
            ],
            "communication": [
                r"\b(?:uart|spi|i2c|can|usb|ethernet|wifi|bluetooth)\b",
                r"\b(?:radio|rf|nrf|lora|zigbee|mesh|gsm|gprs|3g|4g|lte)\b",
                r"\b(?:transmit|receive|communicate|wireless|wired)\b"
            ],
            "display": [
                r"\b(?:display|lcd|oled|tft|e-ink|segment)\b",
                r"\b(?:screen|monitor|show|visualize)\b",
                r"\b(?:ssd\d+|st\d+|ili\d+|nokia)\b"
            ],
            "memory": [
                r"\b(?:memory|storage|eeprom|flash|sd|card)\b",
                r"\b(?:store|save|log|record|data)\b",
                r"\b(?:at24|w25|mx25|microsd)\b"
            ],
            "analog": [
                r"\b(?:adc|dac|amplifier|opamp|comparator)\b",
                r"\b(?:analog|signal|voltage|current|reference)\b",
                r"\b(?:mcp\d+|ads\d+|ina\d+|lm\d+)\b"
            ]
        }
        
        # Constraint patterns
        self.constraint_patterns = {
            "voltage": [
                r"(?:max|maximum|up\s+to)\s+(\d+(?:\.\d+)?)\s*v(?:olts?)?",
                r"(\d+(?:\.\d+)?)\s*v(?:olts?)?\s+(?:max|maximum|or\s+less)",
                r"(?:min|minimum|at\s+least)\s+(\d+(?:\.\d+)?)\s*v(?:olts?)?",
                r"(\d+(?:\.\d+)?)\s*v(?:olts?)?\s+(?:min|minimum|or\s+more)",
                r"(\d+(?:\.\d+)?)\s*v(?:olts?)?\s+(?:supply|power|vcc|vdd)",
                r"(?:3v3|3\.3v|5v|12v|24v)"
            ],
            "size": [
                r"\b(?:small|tiny|compact|miniature)\b",
                r"\b(?:medium|standard|normal)\b",
                r"\b(?:large|big|full-size)\b",
                r"(?:max|maximum)\s+(?:size|dimensions?|footprint)",
                r"(?:min|minimum)\s+(?:size|dimensions?|footprint)"
            ],
            "battery": [
                r"\b(?:lipo|li-po|lithium\s+polymer)\b",
                r"\b(?:li-ion|lithium\s+ion)\b",
                r"\b(?:alkaline|aa|aaa|9v)\b",
                r"\b(?:nimh|ni-mh|nickel)\b",
                r"\b(?:coin|cr\d+|button)\b",
                r"(\d+)\s*mah",
                r"(\d+(?:\.\d+)?)\s*wh"
            ],
            "current": [
                r"(?:max|maximum)\s+(\d+(?:\.\d+)?)\s*(?:ma|milliamps?|a|amps?)",
                r"(\d+(?:\.\d+)?)\s*(?:ma|milliamps?|a|amps?)\s+(?:max|maximum)",
                r"(?:low|minimal)\s+(?:power|current)",
                r"(?:high|peak)\s+(?:power|current)"
            ],
            "frequency": [
                r"(\d+(?:\.\d+)?)\s*(?:mhz|khz|hz)",
                r"(?:clock|frequency|speed)\s+(\d+(?:\.\d+)?)\s*(?:mhz|khz|hz)"
            ]
        }
        
        # Additional patterns for better role detection
        self.communication_patterns = [
            r"\b(?:modbus|rtu|tcp|ethernet|can|lin)\b",
            r"\b(?:rs485|rs232|uart|serial)\b"
        ]
        
        self.encoder_patterns = [
            r"\b(?:encoder|rotary|quadrature)\b",
            r"\b(?:feedback|position|rotation)\b"
        ]
    
    def parse_prompt(self, prompt: str) -> ParsedPrompt:
        """Parse user prompt and extract roles and constraints."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Clean and normalize prompt
        clean_prompt = self._clean_prompt(prompt)
        
        # Extract project name
        project_name = self._extract_project_name(clean_prompt)
        
        # Extract component roles
        roles = self.extract_roles(clean_prompt)
        
        # Extract constraints
        constraints = self.extract_constraints(clean_prompt)
        
        return ParsedPrompt(
            project_name=project_name,
            roles=roles,
            constraints=constraints
        )
    
    def extract_roles(self, prompt: str) -> Dict[str, str]:
        """Extract component roles from prompt using regex patterns."""
        roles = {}
        prompt_lower = prompt.lower()
        
        for role, patterns in self.role_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, prompt_lower, re.IGNORECASE)
                if matches:
                    # Use the first match as the role description
                    if isinstance(matches[0], tuple):
                        role_desc = matches[0][0] if matches[0][0] else matches[0][-1]
                    else:
                        role_desc = matches[0]
                    
                    roles[role] = role_desc
                    break  # Use first matching pattern for each role
        
        # Check for additional communication patterns
        for pattern in self.communication_patterns:
            if re.search(pattern, prompt_lower):
                roles["communication"] = "communication"
                break
        
        # Check for encoder/feedback patterns (should be sensor or analog)
        for pattern in self.encoder_patterns:
            if re.search(pattern, prompt_lower):
                if "analog" not in roles and "sensor" not in roles:
                    roles["analog"] = "encoder"
                break
        
        # Post-process to ensure we have key components
        roles = self._post_process_roles(roles, prompt_lower)
        
        return roles
    
    def extract_constraints(self, prompt: str) -> Dict[str, Any]:
        """Extract technical constraints from prompt."""
        constraints = {}
        prompt_lower = prompt.lower()
        
        # Extract voltage constraints
        voltage_constraints = self._extract_voltage_constraints(prompt_lower)
        constraints.update(voltage_constraints)
        
        # Extract size constraints
        size_constraint = self._extract_size_constraint(prompt_lower)
        if size_constraint:
            constraints["max_size"] = size_constraint
        
        # Extract battery constraints
        battery_constraints = self._extract_battery_constraints(prompt_lower)
        constraints.update(battery_constraints)
        
        # Extract current constraints
        current_constraints = self._extract_current_constraints(prompt_lower)
        constraints.update(current_constraints)
        
        # Extract frequency constraints
        frequency_constraints = self._extract_frequency_constraints(prompt_lower)
        constraints.update(frequency_constraints)
        
        return constraints
    
    def _clean_prompt(self, prompt: str) -> str:
        """Clean and normalize the input prompt."""
        # Remove extra whitespace and normalize
        clean = re.sub(r'\s+', ' ', prompt.strip())
        
        # Remove common filler words that might interfere with parsing
        filler_words = r'\b(?:please|can|you|help|me|with|a|an|the|some|any|would|like|to|want|need)\b'
        clean = re.sub(filler_words, ' ', clean, flags=re.IGNORECASE)
        
        # Normalize common abbreviations
        clean = re.sub(r'\bmcu\b', 'microcontroller', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\btemp\b', 'temperature', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bpwr\b', 'power', clean, flags=re.IGNORECASE)
        
        return clean.strip()
    
    def _extract_project_name(self, prompt: str) -> str:
        """Extract or generate a project name from the prompt."""
        # Look for explicit project names
        project_patterns = [
            r"(?:project|circuit|device|system)\s+(?:called|named|for)\s+([a-zA-Z0-9\s\-_]+)",
            r"([a-zA-Z0-9\s\-_]+)\s+(?:project|circuit|device|system)",
            r"build\s+(?:a|an)\s+([a-zA-Z0-9\s\-_]+)"
        ]
        
        for pattern in project_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) <= 50:
                    return name
        
        # Generate name from key components
        words = []
        if "temperature" in prompt.lower():
            words.append("Temperature")
        if "sensor" in prompt.lower():
            words.append("Sensor")
        if "monitor" in prompt.lower():
            words.append("Monitor")
        if "control" in prompt.lower():
            words.append("Controller")
        if "iot" in prompt.lower():
            words.append("IoT")
        if "wireless" in prompt.lower() or "wifi" in prompt.lower():
            words.append("Wireless")
        
        if words:
            return " ".join(words[:3])  # Limit to 3 words
        
        return "Circuit Project"
    
    def _post_process_roles(self, roles: Dict[str, str], prompt: str) -> Dict[str, str]:
        """Post-process extracted roles to ensure completeness."""
        # If we found sensors but no microcontroller, likely need one
        if "sensor" in roles and "microcontroller" not in roles:
            if any(word in prompt for word in ["read", "monitor", "collect", "data", "iot", "wireless", "station", "system"]):
                roles["microcontroller"] = "controller"
        
        # If we have actuators but no microcontroller, likely need one
        if "actuator" in roles and "microcontroller" not in roles:
            if any(word in prompt for word in ["control", "drive", "switch", "turn", "alarm", "security"]):
                roles["microcontroller"] = "controller"
        
        # If we have communication but no microcontroller, likely need one
        if "communication" in roles and "microcontroller" not in roles:
            roles["microcontroller"] = "controller"
        
        # If we have display/memory/analog but no microcontroller, likely need one
        if any(role in roles for role in ["display", "memory", "analog"]) and "microcontroller" not in roles:
            if any(word in prompt for word in ["device", "instrument", "controller", "system", "measurement"]):
                roles["microcontroller"] = "controller"
        
        # If we have a microcontroller but no explicit power, assume power needed
        if "microcontroller" in roles and "power" not in roles:
            if not any(word in prompt for word in ["usb", "powered", "wall", "adapter"]):
                roles["power"] = "battery"
        
        # If we have sensors and monitoring but no power, likely need power
        if "sensor" in roles and "power" not in roles:
            if any(word in prompt for word in ["station", "monitoring", "system", "device"]):
                roles["power"] = "power"
        
        return roles
    
    def _extract_voltage_constraints(self, prompt: str) -> Dict[str, Any]:
        """Extract voltage constraints from prompt."""
        constraints = {}
        
        # Look for maximum voltage
        max_patterns = [
            r"(?:max|maximum|up\s+to)\s+(\d+(?:\.\d+)?)\s*v",
            r"(\d+(?:\.\d+)?)\s*v\s+(?:max|maximum|or\s+less)"
        ]
        
        for pattern in max_patterns:
            match = re.search(pattern, prompt)
            if match:
                voltage = float(match.group(1))
                if 0 < voltage <= 50:
                    constraints["max_voltage"] = voltage
                break
        
        # Look for minimum voltage
        min_patterns = [
            r"(?:min|minimum|at\s+least)\s+(\d+(?:\.\d+)?)\s*v",
            r"(\d+(?:\.\d+)?)\s*v\s+(?:min|minimum|or\s+more)"
        ]
        
        for pattern in min_patterns:
            match = re.search(pattern, prompt)
            if match:
                voltage = float(match.group(1))
                if 0 < voltage <= 50:
                    constraints["min_voltage"] = voltage
                break
        
        # Look for specific voltage mentions
        if "3v3" in prompt or "3.3v" in prompt:
            constraints["target_voltage"] = 3.3
        elif "24v" in prompt:
            constraints["target_voltage"] = 24.0
        elif "12v" in prompt:
            constraints["target_voltage"] = 12.0
        elif "5v" in prompt:
            constraints["target_voltage"] = 5.0
        
        return constraints
    
    def _extract_size_constraint(self, prompt: str) -> Optional[str]:
        """Extract size constraint from prompt."""
        if any(word in prompt for word in ["small", "tiny", "compact", "miniature", "mini"]):
            return "small"
        elif any(word in prompt for word in ["large", "big", "full-size", "full size"]):
            return "large"
        elif any(word in prompt for word in ["medium", "standard", "normal", "regular"]):
            return "medium"
        
        return None
    
    def _extract_battery_constraints(self, prompt: str) -> Dict[str, Any]:
        """Extract battery-related constraints from prompt."""
        constraints = {}
        
        # Battery type
        if "lipo" in prompt or "li-po" in prompt or "lithium polymer" in prompt:
            constraints["battery_type"] = "lipo"
        elif "li-ion" in prompt or "lithium ion" in prompt:
            constraints["battery_type"] = "li-ion"
        elif "alkaline" in prompt or "aa" in prompt or "aaa" in prompt:
            constraints["battery_type"] = "alkaline"
        elif "coin" in prompt or "button" in prompt or "cr2032" in prompt:
            constraints["battery_type"] = "coin"
        
        # Battery capacity
        mah_match = re.search(r"(\d+)\s*mah", prompt)
        if mah_match:
            constraints["battery_capacity_mah"] = int(mah_match.group(1))
        
        wh_match = re.search(r"(\d+(?:\.\d+)?)\s*wh", prompt)
        if wh_match:
            constraints["battery_capacity_wh"] = float(wh_match.group(1))
        
        return constraints
    
    def _extract_current_constraints(self, prompt: str) -> Dict[str, Any]:
        """Extract current consumption constraints from prompt."""
        constraints = {}
        
        # Maximum current patterns - check in order of specificity
        current_patterns = [
            (r"(?:max|maximum)\s+(\d+(?:\.\d+)?)\s*ma", "ma"),
            (r"(\d+(?:\.\d+)?)\s*ma\s+(?:max|maximum)", "ma"),
            (r"(?:max|maximum)\s+(\d+(?:\.\d+)?)\s*a(?:mps?)?", "a"),
            (r"(\d+(?:\.\d+)?)\s*a(?:mps?)?\s+(?:max|maximum)", "a"),
            (r"(\d+(?:\.\d+)?)\s*a\b", "a")  # Match patterns like "2A"
        ]
        
        for pattern, unit in current_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                current = float(match.group(1))
                if unit == "ma":
                    constraints["max_current_ma"] = current
                else:
                    constraints["max_current_a"] = current
                break
        
        # Power consumption preferences
        if any(word in prompt for word in ["low power", "minimal power", "battery efficient"]):
            constraints["low_power"] = True
        elif any(word in prompt for word in ["high power", "peak power", "maximum performance"]):
            constraints["high_power"] = True
        
        return constraints
    
    def _extract_frequency_constraints(self, prompt: str) -> Dict[str, Any]:
        """Extract frequency/speed constraints from prompt."""
        constraints = {}
        
        freq_patterns = [
            r"(\d+(?:\.\d+)?)\s*mhz",
            r"(\d+(?:\.\d+)?)\s*khz",
            r"(\d+(?:\.\d+)?)\s*hz",
            r"(?:clock|frequency|speed)\s+(\d+(?:\.\d+)?)\s*(?:mhz|khz|hz)"
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, prompt)
            if match:
                freq = float(match.group(1))
                if "mhz" in pattern:
                    constraints["frequency_mhz"] = freq
                elif "khz" in pattern:
                    constraints["frequency_khz"] = freq
                else:
                    constraints["frequency_hz"] = freq
                break
        
        return constraints