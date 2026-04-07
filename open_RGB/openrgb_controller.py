"""
OpenRGB Controller for Assetto Corsa Shift Lights
Integrates with OpenRGB SDK to control RGB devices based on AC telemetry
"""

import sys
import time
import json
from pathlib import Path
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import numpy as np
import os
from dotenv import load_dotenv

# Load .env from root or current directory
load_dotenv(Path(__file__).parent.parent / '.env')
load_dotenv()

try:
    from dynamic_rpm_calculator import DynamicRPMConfig
except ImportError:
    DynamicRPMConfig = None


class OpenRGBShiftLights:
    """Main controller for RGB shift lights in Assetto Corsa"""
    
    def __init__(self, config_path: str = "rgb_config.json"):
        """
        Initialize OpenRGB controller
        
        Args:
            config_path: Path to RGB configuration file
        """
        self.config = self.load_config(config_path)
        self.client = None
        self.devices = {}
        self.is_connected = False
        
        # Initialize dynamic RPM calculator for car-specific thresholds
        self.rpm_config = None
        if DynamicRPMConfig:
            self.rpm_config = DynamicRPMConfig(self.config)
            if self.rpm_config.use_dynamic:
                print(f"✓ Dynamic RPM thresholds enabled (AC car detected)")
            else:
                print(f"⚠ Using static RPM thresholds from config (AC not running)")
        
        self.last_car_update = time.time()
        self.car_update_interval = 5.0  # Check for car change every 5 seconds
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        default_config = {
            "openrgb_host": os.getenv("OPEN_RGB_HOST", "localhost"),
            "openrgb_port": int(os.getenv("OPEN_RGB_PORT", 6742)),
            "shift_light_thresholds": {
                "idle": int(os.getenv("IDLE_RPM", 2000)),
                "warning": int(os.getenv("WARNING_RPM", 6000)),
                "critical": int(os.getenv("CRITICAL_RPM", 8000)),
                "redline": int(os.getenv("REDLINE_RPM", 9000))
            },
            "color_scheme": {
                "idle": [int(x) for x in os.getenv("COLOR_IDLE", "0,255,0").split(',')],
                "warning": [int(x) for x in os.getenv("COLOR_WARNING", "255,255,0").split(',')],
                "critical": [int(x) for x in os.getenv("COLOR_CRITICAL", "255,128,0").split(',')],
                "redline": [int(x) for x in os.getenv("COLOR_REDLINE", "255,0,0").split(',')],
                "off": [int(x) for x in os.getenv("COLOR_OFF", "0,0,0").split(',')]
            },
            "enabled_devices": os.getenv("OPEN_RGB_ENABLED_DEVICES", "").split(',') if os.getenv("OPEN_RGB_ENABLED_DEVICES") else []
        }
        
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            # Create default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default config at {config_file}")
        
        return default_config
    
    def connect(self) -> bool:
        """Connect to OpenRGB server"""
        try:
            address = self.config.get("openrgb_host", "127.0.0.1")
            port = self.config.get("openrgb_port", 6742)
            
            print(f"Connecting to OpenRGB at {address}:{port}...")
            self.client = OpenRGBClient(address=address, port=port)
            self.client.connect()
            
            # Get all connected devices
            device_count = len(self.client.devices)
            print(f"Found {device_count} RGB devices\n")
            
            # Get enabled devices filter (empty list = all devices)
            enabled_devices = self.config.get("enabled_devices", [])
            
            self.devices = []
            for i, device in enumerate(self.client.devices):
                # Check if device should be enabled
                if not enabled_devices or device.name in enabled_devices:
                    try:
                        # Force Direct mode for real-time updates
                        modes = [m.name.lower() for m in device.modes]
                        if 'direct' in modes:
                            direct_idx = modes.index('direct')
                            if device.active_mode != device.modes[direct_idx].name:
                                device.set_mode('direct')
                                print(f"  ✓ Set {device.name} (ID {i}) to Direct mode")
                        
                        led_count = len(device.leds) if hasattr(device, 'leds') else 0
                        print(f"  [ENABLE] Device {i}: {device.name} ({led_count} LEDs)")
                        self.devices.append(device)
                    except Exception as dev_err:
                        print(f"  [WARN] Could not initialize device {i} ({device.name}): {dev_err}")
                else:
                    print(f"  [SKIP] Device {i}: {device.name} (not in enabled_devices)")
            
            print(f"\nUsing {len(self.devices)} device(s) for effects\n")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"Failed to connect to OpenRGB: {e}")
            self.is_connected = False
            return False
    
    def get_current_thresholds(self) -> dict:
        """
        Get current RPM thresholds (dynamic or static)
        
        Returns:
            Dict with idle, warning, critical, redline RPM values
        """
        if self.rpm_config and self.rpm_config.use_dynamic:
            return self.rpm_config.get_thresholds()
        else:
            return self.config.get("shift_light_thresholds", {
                "idle": 2000,
                "warning": 6000,
                "critical": 8000,
                "redline": 9000,
            })
    
    def get_car_info(self) -> dict:
        """Get current car information"""
        if self.rpm_config:
            return self.rpm_config.get_car_info()
        else:
            return {
                "name": "Unknown",
                "max_rpm": 10000,
                "source": "Default",
            }
    
    def check_for_car_change(self) -> bool:
        """
        Check if car changed and update thresholds
        
        Returns:
            True if car changed and was updated
        """
        if not self.rpm_config:
            return False
        
        current_time = time.time()
        if current_time - self.last_car_update < self.car_update_interval:
            return False
        
        self.last_car_update = current_time
        
        old_max_rpm = self.rpm_config.calculator.max_rpm if self.rpm_config else 10000
        
        # Try to update from AC
        if self.rpm_config.update_from_ac():
            new_max_rpm = self.rpm_config.calculator.max_rpm
            if old_max_rpm != new_max_rpm:
                car_info = self.get_car_info()
                print(f"\n🚗 Car changed!")
                print(f"  Car: {car_info['name']}")
                print(f"  MaxRPM: {old_max_rpm} → {new_max_rpm}")
                return True
        
        return False
    
    def disconnect(self):
        """Disconnect from OpenRGB server"""
        if self.client:
            self.client.disconnect()
            self.is_connected = False
    
    def get_rpm_color(self, rpm: int) -> RGBColor:
        """
        Get color based on RPM value (uses dynamic thresholds if available)
        
        Args:
            rpm: Current engine RPM
            
        Returns:
            RGBColor object for the given RPM range
        """
        # Use dynamic thresholds if available, otherwise use static config
        thresholds = self.get_current_thresholds()
        colors = self.config["color_scheme"]
        
        if rpm <= thresholds["idle"]:
            r, g, b = colors["idle"]
        elif rpm <= thresholds["warning"]:
            # Green to yellow gradient
            r, g, b = colors["idle"]
        elif rpm <= thresholds["critical"]:
            # Yellow to orange gradient
            progress = (rpm - thresholds["warning"]) / (thresholds["critical"] - thresholds["warning"])
            yellow = np.array(colors["warning"])
            orange = np.array(colors["critical"])
            color_array = yellow + (orange - yellow) * progress
            r, g, b = map(int, color_array)
        elif rpm <= thresholds["redline"]:
            # Orange to red gradient
            progress = (rpm - thresholds["critical"]) / (thresholds["redline"] - thresholds["critical"])
            orange = np.array(colors["critical"])
            red = np.array(colors["redline"])
            color_array = orange + (red - orange) * progress
            r, g, b = map(int, color_array)
        else:
            # Beyond redline - blinking red
            r, g, b = colors["redline"]
        
        return RGBColor(int(r), int(g), int(b))
    
    def update_shift_lights(self, rpm: int):
        """
        Update all RGB devices based on RPM
        
        Args:
            rpm: Current engine RPM
        """
        if not self.is_connected or not self.client:
            return
        
        color = self.get_rpm_color(rpm)
        
        try:
            # Update all devices
            for device in self.devices:
                device.set_color(color)
                
        except Exception as e:
            print(f"Error updating RGB lights: {e}")
    
    def set_color_all(self, r: int, g: int, b: int):
        """Set all devices to specific color"""
        if not self.is_connected:
            return
        
        color = RGBColor(r, g, b)
        try:
            for device in self.devices:
                device.set_color(color)
        except Exception as e:
            print(f"Error setting color: {e}")
    
    def update_shift_lights_animated(self, color):
        """
        Update all RGB devices with a color (supports animated colors)
        
        Args:
            color: Color object (can be animated from led_animations)
        """
        if not self.is_connected or not self.client:
            return
        
        try:
            # Handle both RGBColor and custom Color objects
            if hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
                rgb_color = RGBColor(int(color.r), int(color.g), int(color.b))
            else:
                rgb_color = color

            for device in self.devices:
                device.set_color(rgb_color)
        except Exception as e:
            print(f"Error updating animated RGB lights: {e}")
    
    def test_colors(self):
        """Cycle through test colors"""
        if not self.is_connected:
            print("Not connected to OpenRGB")
            return
        
        test_colors = [
            (0, 255, 0),    # Green
            (255, 255, 0),  # Yellow
            (255, 128, 0),  # Orange
            (255, 0, 0),    # Red
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Magenta
        ]
        
        print("Testing colors... (press Ctrl+C to stop)")
        try:
            for r, g, b in test_colors:
                self.set_color_all(r, g, b)
                print(f"Color: RGB({r}, {g}, {b})")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Test stopped")
            self.set_color_all(0, 0, 0)


if __name__ == "__main__":
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        # Test the colors
        controller.test_colors()
        
        # Example: simulate RPM changes
        print("\nSimulating RPM changes...")
        for rpm in [2000, 4000, 6000, 7000, 8000, 9000, 9500]:
            controller.update_shift_lights(rpm)
            print(f"RPM: {rpm}")
            time.sleep(1)
        
        # Turn off
        controller.set_color_all(0, 0, 0)
        controller.disconnect()
    else:
        print("Failed to connect. Make sure OpenRGB SDK server is running.")
        print("Download from: https://github.com/CalcProgrammer1/OpenRGB")
