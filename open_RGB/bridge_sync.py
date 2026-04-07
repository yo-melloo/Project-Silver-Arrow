"""
Argentum Bridge Sync
Sincroniza dados de RPM máximo com o dashboard web via argentum_bridge
Allows OpenRGB to get car data from the same source as the web dashboard
"""

import json
import asyncio
import threading
import time
from typing import Dict, Optional, Callable
from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root or current directory
load_dotenv(Path(__file__).parent.parent / '.env')
load_dotenv()

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


@dataclass
class CarTelemetry:
    """Car telemetry data from Argentum Bridge"""
    max_rpm: int
    car_name: str
    rpm: int
    speed: float
    gear: int
    throttle: float
    brake: float
    timestamp: float = 0.0


class ArgentumBridgeSyncClient:
    """
    Client to sync with Argentum Bridge WebSocket
    Gets real-time car data including maxRpm
    """
    
    def __init__(self, bridge_url: str = None):
        """
        Initialize bridge sync client
        
        Args:
            bridge_url: WebSocket URL of Argentum Bridge (optional, defaults to BRIDGE_HOST:BRIDGE_PORT)
        """
        if not bridge_url:
            host = os.getenv("BRIDGE_HOST", "localhost")
            port = os.getenv("BRIDGE_PORT", "8001")
            self.bridge_url = f"ws://{host}:{port}/ws"
        else:
            self.bridge_url = bridge_url
            
        self.is_connected = False
        self.latest_data = None
        self.callbacks = []
        self.thread = None
        self.stop_event = threading.Event()
        
        if not WEBSOCKETS_AVAILABLE:
            print("⚠ websockets not installed - Bridge sync disabled")
            print("  Install with: pip install websockets")
    
    def add_callback(self, callback: Callable):
        """
        Add callback to be called when new data arrives
        
        Args:
            callback: Function(telemetry: CarTelemetry) to call
        """
        self.callbacks.append(callback)
    
    async def _connect_and_listen(self):
        """Main connection loop (async)"""
        while not self.stop_event.is_set():
            try:
                async with websockets.connect(self.bridge_url, ping_interval=None) as websocket:
                    self.is_connected = True
                    print(f"✓ Connected to Argentum Bridge: {self.bridge_url}")
                    
                    async for message in websocket:
                        if self.stop_event.is_set():
                            break
                        
                        try:
                            data = json.loads(message)
                            
                            # Extract telemetry
                            telemetry = CarTelemetry(
                                max_rpm=data.get("maxRpm", 10000),
                                car_name=data.get("car", "Unknown"),
                                rpm=data.get("rpm", 0),
                                speed=data.get("speed", 0.0),
                                gear=data.get("gear", 0),
                                throttle=data.get("throttle", 0.0),
                                brake=data.get("brake", 0.0),
                                timestamp=time.time(),
                            )
                            
                            self.latest_data = telemetry
                            
                            # Call callbacks
                            for callback in self.callbacks:
                                try:
                                    callback(telemetry)
                                except Exception as e:
                                    pass  # Silently ignore callback errors
                        
                        except json.JSONDecodeError:
                            pass  # Ignore malformed JSON
                        except Exception as e:
                            pass  # Silently ignore
            
            except Exception as e:
                self.is_connected = False
                if not self.stop_event.is_set():
                    await asyncio.sleep(2)  # Retry after 2 seconds
    
    def _run_event_loop(self):
        """Run asyncio event loop in thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._connect_and_listen())
        finally:
            loop.close()
    
    def start(self) -> bool:
        """
        Start sync client in background thread
        
        Returns:
            True if started successfully
        """
        if not WEBSOCKETS_AVAILABLE:
            print("✗ websockets library not available")
            return False
        
        if self.thread and self.thread.is_alive():
            return True  # Already running
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        # Wait a bit for connection
        for _ in range(10):
            if self.is_connected:
                return True
            time.sleep(0.1)
        
        return False
    
    def stop(self):
        """Stop sync client"""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
    
    def get_latest_data(self) -> Optional[CarTelemetry]:
        """Get latest telemetry data"""
        return self.latest_data
    
    def get_max_rpm(self) -> int:
        """Get max RPM from latest data"""
        if self.latest_data:
            return self.latest_data.max_rpm
        return 10000
    
    def get_car_name(self) -> str:
        """Get car name from latest data"""
        if self.latest_data:
            return self.latest_data.car_name
        return "Unknown"


class BridgeSyncManager:
    """
    Manages sync with Argentum Bridge
    Integrates car data for OpenRGB thresholds
    """
    
    def __init__(self, on_car_data_callback: Optional[Callable] = None):
        """
        Initialize bridge sync manager
        
        Args:
            on_car_data_callback: Callback function when car data updates
        """
        self.client = None
        self.on_car_data = on_car_data_callback
        self.last_max_rpm = None
        self.last_car_name = None
        
        if WEBSOCKETS_AVAILABLE:
            self.client = ArgentumBridgeSyncClient()
            self.client.add_callback(self._on_telemetry)
    
    def _on_telemetry(self, telemetry: CarTelemetry):
        """Handle telemetry update"""
        # Check if car changed
        if (telemetry.max_rpm != self.last_max_rpm or 
            telemetry.car_name != self.last_car_name):
            self.last_max_rpm = telemetry.max_rpm
            self.last_car_name = telemetry.car_name
            
            if self.on_car_data:
                self.on_car_data({
                    "max_rpm": telemetry.max_rpm,
                    "car_name": telemetry.car_name,
                })
    
    def start(self) -> bool:
        """Start sync"""
        if self.client:
            return self.client.start()
        return False
    
    def stop(self):
        """Stop sync"""
        if self.client:
            self.client.stop()
    
    def get_max_rpm(self) -> int:
        """Get current max RPM"""
        if self.client:
            return self.client.get_max_rpm()
        return 10000


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("Argentum Bridge Sync Test")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("✗ websockets not installed")
        print("  Install with: pip install websockets")
    else:
        def on_data(data):
            print(f"\n✓ Car data received:")
            print(f"  Car: {data['car_name']}")
            print(f"  MaxRPM: {data['max_rpm']}")
        
        manager = BridgeSyncManager(on_car_data_callback=on_data)
        
        print("\nStarting sync...")
        if manager.start():
            print("✓ Connected to Argentum Bridge")
            
            try:
                for i in range(10):
                    max_rpm = manager.get_max_rpm()
                    print(f"  Current maxRPM: {max_rpm}")
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                manager.stop()
        else:
            print("✗ Failed to connect to Argentum Bridge")
            print("  Make sure argentum_bridge is running on http://localhost:8001")
    
    print("\n" + "=" * 60)
