"""
LED Animation Effects for OpenRGB Shift Lights
Provides pulsing, color transitions, and RPM-based animations
"""

import time
import math
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np
from openrgb.utils import RGBColor


class RPMState(Enum):
    """RPM state classification"""
    IDLE = "idle"              # RPM stable at low range
    NORMAL = "normal"          # RPM steady in normal range
    RISING = "rising"          # RPM increasing (yellow warning)
    CRITICAL = "critical"      # RPM high but steady (orange)
    FORCED = "forced"          # RPM being pushed hard (red pulsing)
    PAST_REDLINE = "redline"   # Beyond max RPM (red pulsing fast)


@dataclass
class AnimationConfig:
    """Configuration for LED animations"""
    
    # Pulse animation
    pulse_frequency: float = 2.0  # Hz (2 pulses per second)
    pulse_min_brightness: float = 0.2  # Min brightness factor (0.0-1.0)
    
    # Rising RPM detection
    rising_threshold: float = 500.0  # RPM/frame increase to trigger rising state
    rising_smoothing: int = 5  # Frames to average for trend detection
    
    # Color transition
    smooth_transition_frames: int = 10  # Frames to smoothly transition colors


class RPMTrendDetector:
    """Detects RPM trends to classify current driving state"""
    
    def __init__(self, window_size: int = 5):
        """
        Initialize trend detector
        
        Args:
            window_size: Number of RPM samples to keep for trend analysis
        """
        self.window_size = window_size
        self.rpm_history: List[int] = []
        self.timestamp_history: List[float] = []
        
    def add_sample(self, rpm: int, timestamp: float = None):
        """
        Add RPM sample
        
        Args:
            rpm: Current RPM value
            timestamp: Sample timestamp (uses time.time() if None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.rpm_history.append(rpm)
        self.timestamp_history.append(timestamp)
        
        # Keep only recent samples
        if len(self.rpm_history) > self.window_size:
            self.rpm_history.pop(0)
            self.timestamp_history.pop(0)
    
    def get_rpm_change_rate(self) -> float:
        """
        Get RPM change rate (RPM per second)
        
        Returns:
            RPM change rate, or 0 if not enough data
        """
        if len(self.rpm_history) < 2:
            return 0.0
        
        rpm_change = self.rpm_history[-1] - self.rpm_history[0]
        time_change = self.timestamp_history[-1] - self.timestamp_history[0]
        
        if time_change <= 0:
            return 0.0
        
        return rpm_change / time_change
    
    def get_avg_rpm_change_rate(self) -> float:
        """Get smoothed RPM change rate"""
        if len(self.rpm_history) < 2:
            return 0.0
        
        rates = []
        for i in range(1, len(self.rpm_history)):
            time_delta = self.timestamp_history[i] - self.timestamp_history[i-1]
            if time_delta > 0:
                rate = (self.rpm_history[i] - self.rpm_history[i-1]) / time_delta
                rates.append(rate)
        
        return np.mean(rates) if rates else 0.0
    
    def is_rising(self, threshold: float = 500.0) -> bool:
        """
        Check if RPM is rising above threshold
        
        Args:
            threshold: RPM/second change threshold
            
        Returns:
            True if RPM is rising significantly
        """
        return self.get_avg_rpm_change_rate() > threshold


class AnimationPlayer:
    """Manages animation playback with timing"""
    
    def __init__(self, animation_config: AnimationConfig = None):
        """
        Initialize animation player
        
        Args:
            animation_config: Animation configuration
        """
        self.config = animation_config or AnimationConfig()
        self.start_time = time.time()
        self.current_time = self.start_time
        self.is_playing = True
        
    def update(self, elapsed_time: float = None):
        """Update animation time"""
        if elapsed_time is not None:
            self.current_time = self.start_time + elapsed_time
        else:
            self.current_time = time.time()
    
    def get_pulse_factor(self, frequency: float = None, 
                         min_brightness: float = None) -> float:
        """
        Get current pulse factor (0.0 to 1.0)
        
        Args:
            frequency: Pulse frequency in Hz
            min_brightness: Minimum brightness factor
            
        Returns:
            Brightness factor (0.0 to 1.0)
        """
        freq = frequency or self.config.pulse_frequency
        min_bright = min_brightness or self.config.pulse_min_brightness
        
        # Sinusoidal pulse: goes from min to max and back
        elapsed = (self.current_time - self.start_time) * 2 * math.pi * freq
        sine_value = math.sin(elapsed)  # -1 to 1
        
        # Map from [-1, 1] to [min_brightness, 1.0]
        pulse = min_bright + (1.0 - min_bright) * (sine_value + 1) / 2
        return pulse
    
    def get_blink_factor(self, frequency: float = 2.0) -> float:
        """
        Get blink factor (on/off)
        
        Args:
            frequency: Blink frequency in Hz
            
        Returns:
            1.0 (on) or 0.0 (off)
        """
        period = 1.0 / frequency
        phase = (self.current_time - self.start_time) % period
        return 1.0 if phase < period / 2 else 0.0


class LEDAnimator:
    """Applies animations to colors based on RPM state"""
    
    def __init__(self, animation_config: AnimationConfig = None):
        """
        Initialize LED animator
        
        Args:
            animation_config: Animation configuration
        """
        self.config = animation_config or AnimationConfig()
        self.player = AnimationPlayer(self.config)
        self.trend_detector = RPMTrendDetector(self.config.rising_smoothing)
        
        # Color transition state
        self.current_color = RGBColor(0, 255, 0)  # Start green
        self.target_color = RGBColor(0, 255, 0)
        self.color_transition_progress = 1.0
        
    def update(self, elapsed_time: float = None):
        """Update animation state"""
        self.player.update(elapsed_time)
    
    def classify_rpm_state(self, rpm: int, thresholds: dict) -> RPMState:
        """
        Classify current RPM state
        
        Args:
            rpm: Current RPM
            thresholds: RPM thresholds dict with keys: idle, warning, critical, redline
            
        Returns:
            RPMState classification
        """
        # Add sample for trend detection
        self.trend_detector.add_sample(rpm)
        
        # Check if RPM is rising
        if self.trend_detector.is_rising(self.config.rising_threshold):
            return RPMState.RISING
        
        # Classify by absolute RPM
        if rpm >= thresholds["redline"]:
            return RPMState.PAST_REDLINE
        elif rpm >= thresholds["critical"]:
            return RPMState.FORCED
        elif rpm >= thresholds["warning"]:
            return RPMState.CRITICAL
        elif rpm >= thresholds["idle"]:
            return RPMState.NORMAL
        else:
            return RPMState.IDLE
    
    def apply_animation(self, color: RGBColor, rpm_state: RPMState) -> RGBColor:
        """
        Apply animation effect to color based on RPM state
        
        Args:
            color: Base color
            rpm_state: Current RPM state
            
        Returns:
            Animated color with effects applied
        """
        if rpm_state == RPMState.IDLE or rpm_state == RPMState.NORMAL:
            # Steady, no animation
            return color
        
        elif rpm_state == RPMState.RISING:
            # Yellow with slight pulse to draw attention
            pulse = self.player.get_pulse_factor(frequency=1.5, min_brightness=0.6)
            return RGBColor(
                int(color.red * pulse),
                int(color.green * pulse),
                int(color.blue * pulse)
            )
        
        elif rpm_state == RPMState.CRITICAL:
            # Orange steady with very subtle pulse
            pulse = self.player.get_pulse_factor(frequency=0.8, min_brightness=0.85)
            return RGBColor(
                int(color.red * pulse),
                int(color.green * pulse),
                int(color.blue * pulse)
            )
        
        elif rpm_state == RPMState.FORCED:
            # Red pulsing moderately
            pulse = self.player.get_pulse_factor(frequency=2.5, min_brightness=0.3)
            return RGBColor(
                int(color.red * pulse),
                int(color.green * pulse),
                int(color.blue * pulse)
            )
        
        elif rpm_state == RPMState.PAST_REDLINE:
            # Red blinking fast (warning)
            pulse = self.player.get_pulse_factor(frequency=4.0, min_brightness=0.1)
            return RGBColor(
                int(color.red * pulse),
                int(color.green * pulse),
                int(color.blue * pulse)
            )
        
        return color
    
    def interpolate_color(self, color1: Tuple[int, int, int], 
                         color2: Tuple[int, int, int], 
                         progress: float) -> Tuple[int, int, int]:
        """
        Interpolate between two colors
        
        Args:
            color1: Start color (R, G, B)
            color2: End color (R, G, B)
            progress: Interpolation progress (0.0 to 1.0)
            
        Returns:
            Interpolated color
        """
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


if __name__ == "__main__":
    # Test animations
    animator = LEDAnimator()
    
    thresholds = {
        "idle": 2000,
        "warning": 6000,
        "critical": 8000,
        "redline": 9000
    }
    
    print("Testing LED Animations\n")
    
    # Simulate RPM progression
    test_rpms = [1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 8500, 9000, 9500]
    
    for i, rpm in enumerate(test_rpms):
        animator.update(elapsed_time=i * 0.1)
        
        state = animator.classify_rpm_state(rpm, thresholds)
        
        # Create base color (just show which state)
        if state == RPMState.IDLE:
            base_color = RGBColor(0, 255, 0)
        elif state == RPMState.RISING:
            base_color = RGBColor(255, 255, 0)
        elif state == RPMState.NORMAL:
            base_color = RGBColor(100, 200, 0)
        elif state == RPMState.CRITICAL:
            base_color = RGBColor(255, 128, 0)
        elif state == RPMState.FORCED:
            base_color = RGBColor(255, 0, 0)
        else:
            base_color = RGBColor(255, 0, 0)
        
        animated = animator.apply_animation(base_color, state)
        
        print(f"RPM: {rpm:5d} | State: {state.value:12s} | "
              f"Color: RGB({animated.red:3d}, {animated.green:3d}, {animated.blue:3d})")
