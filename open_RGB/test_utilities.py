"""
Test utilities for OpenRGB Shift Lights Integration
Provided functionality for testing, debugging, and visualization
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts_python"))

from openrgb_controller import OpenRGBShiftLights


def test_device_detection():
    """Test and list all connected RGB devices"""
    print("=== OpenRGB Device Detection ===\n")
    
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        print(f"✓ Connected to OpenRGB SDK Server")
        print(f"  Host: {controller.config.get('openrgb_host', 'localhost')}")
        print(f"  Port: {controller.config.get('openrgb_port', 6742)}\n")
        
        print(f"Found {len(controller.devices)} device(s):\n")
        
        for i, (name, device) in enumerate(controller.devices.items(), 1):
            print(f"{i}. {name}")
            print(f"   Type: {device.type}")
            print(f"   LEDs: {len(device.leds)}")
            try:
                print(f"   Zones: {len(device.zones)}")
            except:
                pass
            print()
        
        controller.disconnect()
    else:
        print("✗ Failed to connect to OpenRGB Server")
        print("  Make sure OpenRGB is running and SDK Server is enabled")


def test_color_gradients():
    """Test color gradients from green → yellow → orange → red"""
    print("=== Color Gradient Test ===\n")
    
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        print("Testing color gradients based on RPM...\n")
        
        # Simulate RPM from idle to redline
        rpm_values = [
            (2000, "Idle (Green)"),
            (4000, "Low RPM"),
            (6000, "Warning (Yellow)"),
            (7000, "Rising"),
            (8000, "Critical (Orange)"),
            (8500, "Near Redline"),
            (9000, "Redline (Red)"),
            (9500, "Over Redline"),
        ]
        
        for rpm, description in rpm_values:
            color = controller.get_rpm_color(rpm)
            controller.update_shift_lights(rpm)
            
            # Create visual bar
            bar_length = int(rpm / 100)
            bar = "█" * min(bar_length, 95)
            
            print(f"{rpm:5d} RPM | {bar} | {description}")
            print(f"        Color: RGB({color.red}, {color.green}, {color.blue})")
            
            time.sleep(0.5)
        
        # Turn off
        controller.set_color_all(0, 0, 0)
        controller.disconnect()
        print("\n✓ Test completed")
    else:
        print("✗ Failed to connect to OpenRGB Server")


def test_individual_colors():
    """Test individual colors"""
    print("=== Individual Color Test ===\n")
    
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        colors = [
            ((0, 255, 0), "Green"),
            ((255, 255, 0), "Yellow"),
            ((255, 128, 0), "Orange"),
            ((255, 0, 0), "Red"),
            ((0, 0, 255), "Blue"),
            ((255, 0, 255), "Magenta"),
            ((0, 255, 255), "Cyan"),
            ((255, 255, 255), "White"),
        ]
        
        for (r, g, b), name in colors:
            controller.set_color_all(r, g, b)
            print(f"■ {name:10} RGB({r:3}, {g:3}, {b:3})")
            time.sleep(0.8)
        
        # Turn off
        controller.set_color_all(0, 0, 0)
        controller.disconnect()
        print("\n✓ Color test completed")
    else:
        print("✗ Failed to connect to OpenRGB Server")


def test_blinking_effect():
    """Test blinking effect (useful for alerts)"""
    print("=== Blinking Effect Test ===\n")
    
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        print("Red blinking (redline alert)...\n")
        
        for i in range(6):
            controller.set_color_all(255, 0, 0)
            print("█ ON")
            time.sleep(0.3)
            
            controller.set_color_all(0, 0, 0)
            print("  OFF")
            time.sleep(0.3)
        
        controller.disconnect()
        print("\n✓ Blinking test completed")
    else:
        print("✗ Failed to connect to OpenRGB Server")


def test_performance():
    """Test update frequency and performance"""
    print("=== Performance Test ===\n")
    
    controller = OpenRGBShiftLights()
    
    if controller.connect():
        print("Testing update rate with different intervals...\n")
        
        intervals = [0.001, 0.005, 0.01, 0.02, 0.05]
        
        for interval in intervals:
            start = time.time()
            updates = 0
            
            target_duration = 1.0
            while time.time() - start < target_duration:
                controller.update_shift_lights(5000)  # Fixed RPM
                updates += 1
                time.sleep(interval)
            
            actual_rate = updates / (time.time() - start)
            print(f"Interval {interval*1000:5.1f}ms → {actual_rate:.1f} updates/sec")
        
        controller.disconnect()
        print("\n✓ Performance test completed")
    else:
        print("✗ Failed to connect to OpenRGB Server")


def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("OpenRGB Shift Lights - Test Utilities")
    print("="*50 + "\n")
    
    tests = [
        ("1", "Device Detection", test_device_detection),
        ("2", "Color Gradients", test_color_gradients),
        ("3", "Individual Colors", test_individual_colors),
        ("4", "Blinking Effect", test_blinking_effect),
        ("5", "Performance Test", test_performance),
        ("0", "Run All Tests", None),
    ]
    
    print("Available tests:\n")
    for key, name, _ in tests:
        print(f"  {key}. {name}")
    
    print("\nSelect a test (or press Enter for Interactive mode):")
    
    choice = input("> ").strip().lower()
    
    print()
    
    if choice == "0":
        for key, name, func in tests[:-1]:
            print(f"\nRunning: {name}")
            print("-" * 50)
            func()
            time.sleep(2)
    else:
        for key, name, func in tests:
            if key == choice:
                func()
                break
        else:
            # Interactive mode with all tests
            while True:
                print("\nSelect test (1-5) or 'q' to quit: ", end="")
                choice = input().strip().lower()
                
                if choice == "q":
                    break
                
                for key, name, func in tests[:-1]:
                    if key == choice:
                        print()
                        func()
                        break


if __name__ == "__main__":
    main()
