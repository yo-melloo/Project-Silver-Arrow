"""
Assetto Corsa + OpenRGB Shift Lights Integration
Reads AC telemetry and controls RGB devices in real-time
"""

import os
import sys
import time
import mmap
import struct
from pathlib import Path
from threading import Thread, Event
import logging

# Add parent directory to path for argentum imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts_python"))

from openrgb_controller import OpenRGBShiftLights
from led_animations import LEDAnimator, RPMState, AnimationConfig
from openrgb.utils import RGBColor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ACTelemetryReader:
    """Reads Assetto Corsa shared memory telemetry"""
    
    # Memory map names
    PHYSICS_MAP = "Local\\acpmf_physics"
    STATIC_MAP = "Local\\acpmf_static"
    
    # Offset constants
    RPM_OFFSET = 20
    SPEED_OFFSET = 28
    GEAR_OFFSET = 16
    
    def __init__(self):
        self.current_telemetry = {
            "rpm": 0,
            "speed": 0.0,
            "gear": 0,
            "throttle": 0.0,
            "brake": 0.0,
        }
        self.is_running = False
        
    def read_int(self, data: bytes, offset: int) -> int:
        """Read integer from bytes"""
        return struct.unpack_from('i', data, offset)[0]
    
    def read_float(self, data: bytes, offset: int) -> float:
        """Read float from bytes"""
        return struct.unpack_from('f', data, offset)[0]
    
    def read_telemetry(self) -> bool:
        """
        Read current telemetry from AC shared memory
        Returns True if successful, False if AC is not running
        """
        try:
            with mmap.mmap(-1, 1024, self.PHYSICS_MAP) as physics_map:
                physics_data = physics_map[:]
                
                self.current_telemetry["rpm"] = self.read_int(physics_data, self.RPM_OFFSET)
                self.current_telemetry["speed"] = self.read_float(physics_data, self.SPEED_OFFSET)
                self.current_telemetry["gear"] = self.read_int(physics_data, self.GEAR_OFFSET)
                self.current_telemetry["throttle"] = self.read_float(physics_data, 4)
                self.current_telemetry["brake"] = self.read_float(physics_data, 8)
                
                return True
        except Exception as e:
            return False
    
    def get_telemetry(self) -> dict:
        """Get current telemetry data"""
        return self.current_telemetry.copy()


class ACRGBIntegration:
    """Main integration between AC and OpenRGB"""
    
    def __init__(self, update_interval: float = 0.016):  # ~60 FPS
        """
        Initialize integration
        
        Args:
            update_interval: Update frequency in seconds
        """
        self.telemetry_reader = ACTelemetryReader()
        self.rgb_controller = OpenRGBShiftLights()
        self.update_interval = update_interval
        
        # Initialize LED animator with config from rgb_config.json
        anim_config = self._create_animation_config()
        self.animator = LEDAnimator(anim_config)
        self.animations_enabled = self.rgb_controller.config.get("animations", {}).get("enabled", True)
        
        self.is_running = False
        self.stop_event = Event()
        self.thread = None
        
        # Statistics
        self.stats = {
            "updates": 0,
            "errors": 0,
            "ac_disconnects": 0,
        }
    
    def _create_animation_config(self) -> AnimationConfig:
        """Create animation config from rgb_config.json"""
        anim_settings = self.rgb_controller.config.get("animations", {})
        return AnimationConfig(
            pulse_frequency=anim_settings.get("pulse_frequency", 2.0),
            pulse_min_brightness=anim_settings.get("pulse_min_brightness", 0.2),
            rising_threshold=anim_settings.get("rising_threshold", 500.0),
            rising_smoothing=anim_settings.get("rising_smoothing", 5),
            smooth_transition_frames=anim_settings.get("smooth_transition_frames", 10),
        )
    
    def connect(self) -> bool:
        """Connect to OpenRGB server"""
        logger.info("Connecting to OpenRGB...")
        return self.rgb_controller.connect()
    
    def disconnect(self):
        """Disconnect from OpenRGB"""
        logger.info("Disconnecting from OpenRGB...")
        self.rgb_controller.disconnect()
    
    def run(self):
        """Main integration loop (runs in thread)"""
        self.is_running = True
        self.stop_event.clear()
        
        ac_was_running = False
        last_rpm = 0
        last_rpm_state = RPMState.IDLE
        frame_count = 0
        
        logger.info("Integration loop started")
        if self.animations_enabled:
            logger.info("LED Animations ENABLED")
        else:
            logger.info("LED Animations DISABLED")
        
        # Show initial car info
        car_info = self.rgb_controller.get_car_info()
        logger.info(f"Car: {car_info['name']} (maxRPM: {car_info['max_rpm']}) - {car_info['source']}")
        
        while not self.stop_event.is_set():
            try:
                # Try to read AC telemetry
                if self.telemetry_reader.read_telemetry():
                    ac_was_running = True
                    telemetry = self.telemetry_reader.get_telemetry()
                    
                    rpm = telemetry["rpm"]
                    frame_count += 1
                    
                    # Check for car change (every 5 seconds)
                    if self.rgb_controller.check_for_car_change():
                        car_info = self.rgb_controller.get_car_info()
                        logger.info(f"Updated to: {car_info['name']} (maxRPM: {car_info['max_rpm']})")
                    
                    # Update animator
                    self.animator.update()
                    
                    # Get base color from RPM
                    base_color = self.rgb_controller.get_rpm_color(rpm)
                    
                    # Classify RPM state and apply animations (use dynamic thresholds)
                    rpm_state = self.animator.classify_rpm_state(
                        rpm, 
                        self.rgb_controller.get_current_thresholds()
                    )
                    
                    # Apply animation if enabled
                    if self.animations_enabled:
                        animated_color = self.animator.apply_animation(base_color, rpm_state)
                    else:
                        animated_color = base_color
                    
                    # Update RGB lights with animated color
                    self.rgb_controller.update_shift_lights_animated(animated_color)
                    
                    # Log state changes
                    if rpm_state != last_rpm_state or rpm != last_rpm:
                        state_text = self._format_rpm_state(rpm_state)
                        
                        if rpm % 500 == 0 or rpm_state != last_rpm_state:
                            logger.debug(
                                f"RPM: {rpm:5d} | State: {state_text:10s} | "
                                f"Speed: {telemetry['speed']:6.1f} km/h | "
                                f"Throttle: {telemetry['throttle']:.2f}"
                            )
                    
                    last_rpm = rpm
                    last_rpm_state = rpm_state
                    self.stats["updates"] += 1
                    
                else:
                    # AC not running
                    if ac_was_running:
                        logger.warning("AC disconnected - RGB lights off")
                        self.rgb_controller.set_color_all(0, 0, 0)
                        ac_was_running = False
                        last_rpm_state = RPMState.IDLE
                        self.stats["ac_disconnects"] += 1
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
                self.stats["errors"] += 1
                time.sleep(0.1)
        
        # Cleanup on exit
        self.rgb_controller.set_color_all(0, 0, 0)
        self.is_running = False
        logger.info("Integration loop stopped")
    
    def _format_rpm_state(self, state: RPMState) -> str:
        """Format RPM state for logging"""
        state_emoji = {
            RPMState.IDLE: "🟢",
            RPMState.NORMAL: "🟢",
            RPMState.RISING: "🟡",
            RPMState.CRITICAL: "🟠",
            RPMState.FORCED: "🔴",
            RPMState.PAST_REDLINE: "🔴⚠️",
        }
        return f"{state_emoji.get(state, '?')} {state.value}"
    
    def start(self):
        """Start integration in background thread"""
        if self.is_running:
            logger.warning("Integration already running")
            return
        
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()
        logger.info("Integration thread started")
    
    def stop(self):
        """Stop integration"""
        if not self.is_running:
            return
        
        logger.info("Stopping integration...")
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        self.disconnect()
    
    def print_stats(self):
        """Print integration statistics"""
        print("\n=== Integration Statistics ===")
        print(f"Updates: {self.stats['updates']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"AC Disconnects: {self.stats['ac_disconnects']}")
        print("=" * 30)


def main():
    """Main entry point"""
    logger.info("Starting AC + OpenRGB Integration")
    
    # Create integration
    integration = ACRGBIntegration()
    
    # Connect to OpenRGB
    if not integration.connect():
        logger.error("Failed to connect to OpenRGB SDK server")
        logger.info("Make sure OpenRGB is running: https://github.com/CalcProgrammer1/OpenRGB")
        return
    
    # Start integration
    integration.start()
    
    try:
        logger.info("Integration running... Press Ctrl+C to stop")
        logger.info("Start Assetto Corsa to see shift lights in action")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupt received")
    finally:
        integration.stop()
        integration.print_stats()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
