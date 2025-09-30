"""
IoT Hardware Simulation Layer
============================
This module provides mock hardware components for simulating the Laura-bot IoT project
without requiring physical Arduino boards, cameras, or other hardware.
"""

import time
import random
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import tkinter as tk
from tkinter import ttk
import json


class MockArduino:
    """Mock Arduino board for servo simulation"""
    
    def __init__(self, port: str = 'COM7'):
        self.port = port
        self.is_connected = True
        self.digital_pins = {}
        self.servo_positions = {}
        self.connection_time = datetime.now()
        print(f"🔌 Mock Arduino connected to {port}")
        
        # Initialize digital pins
        for i in range(20):
            self.digital_pins[i] = MockDigitalPin(i)
    
    @property
    def digital(self):
        return self.digital_pins
    
    def exit(self):
        self.is_connected = False
        print("🔌 Mock Arduino disconnected")


class MockDigitalPin:
    """Mock digital pin for servo control"""
    
    def __init__(self, pin_number: int):
        self.pin_number = pin_number
        self.mode = 0  # 0=input, 1=output, 4=servo
        self.value = 0
        self.servo_angle = 0
        
    def write(self, value):
        """Write value to pin (servo angle for servo mode)"""
        if self.mode == 4:  # Servo mode
            self.servo_angle = value
            print(f"🤖 Servo Pin {self.pin_number}: Moving to {value}°")
        else:
            self.value = value
            print(f"📡 Digital Pin {self.pin_number}: {value}")


class MockCamera:
    """Mock camera for gesture simulation"""
    
    def __init__(self, source="http://10.170.105.110:81/stream"):
        self.source = source
        self.is_active = True
        self.current_gesture = "Unknown"
        self.frame_count = 0
        self.simulated_gestures = [
            "Hi", "Ambulance", "Fire", "Sick", "Water", 
            "Up", "Down", "Danger", "Stop", "Wait", "Unknown"
        ]
        print(f"📹 Mock Camera initialized: {source}")
    
    def read(self):
        """Simulate camera frame reading"""
        if not self.is_active:
            return False, None
        
        self.frame_count += 1
        # Simulate random gesture detection every 5 seconds
        if self.frame_count % 150 == 0:
            self.current_gesture = random.choice(self.simulated_gestures)
            print(f"👋 Detected gesture: {self.current_gesture}")
        
        return True, f"Mock Frame {self.frame_count}"
    
    def release(self):
        self.is_active = False
        print("📹 Mock Camera released")


class MockSensorData:
    """Mock environmental sensors"""
    
    def __init__(self):
        self.temperature = 25.0
        self.humidity = 60.0
        self.light_level = 500
        self.noise_level = 45
        self.motion_detected = False
        self.last_update = datetime.now()
        
        # Start background simulation
        self.simulation_thread = threading.Thread(target=self._simulate_sensors, daemon=True)
        self.simulation_thread.start()
    
    def _simulate_sensors(self):
        """Continuously simulate sensor data"""
        while True:
            # Simulate realistic environmental changes
            self.temperature += random.uniform(-0.5, 0.5)
            self.temperature = max(15, min(35, self.temperature))
            
            self.humidity += random.uniform(-2, 2)
            self.humidity = max(30, min(90, self.humidity))
            
            self.light_level += random.randint(-50, 50)
            self.light_level = max(0, min(1000, self.light_level))
            
            self.noise_level += random.uniform(-5, 5)
            self.noise_level = max(20, min(80, self.noise_level))
            
            # Random motion detection
            self.motion_detected = random.random() < 0.1
            
            self.last_update = datetime.now()
            time.sleep(2)
    
    def get_all_data(self) -> Dict:
        """Get all sensor readings"""
        return {
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "light_level": self.light_level,
            "noise_level": round(self.noise_level, 1),
            "motion_detected": self.motion_detected,
            "timestamp": self.last_update.isoformat()
        }


class IoTDeviceManager:
    """Manages all IoT devices and their states"""
    
    def __init__(self):
        self.devices = {
            "arduino_main": MockArduino("COM7"),
            "camera": MockCamera(),
            "sensors": MockSensorData()
        }
        self.device_status = {}
        self.connection_log = []
        self._update_device_status()
    
    def _update_device_status(self):
        """Update device connection status"""
        self.device_status = {
            "arduino_main": {
                "connected": self.devices["arduino_main"].is_connected,
                "port": self.devices["arduino_main"].port,
                "uptime": (datetime.now() - self.devices["arduino_main"].connection_time).seconds
            },
            "camera": {
                "active": self.devices["camera"].is_active,
                "source": self.devices["camera"].source,
                "current_gesture": self.devices["camera"].current_gesture
            },
            "sensors": {
                "data": self.devices["sensors"].get_all_data(),
                "last_update": self.devices["sensors"].last_update.isoformat()
            }
        }
    
    def get_device_status(self) -> Dict:
        """Get status of all devices"""
        self._update_device_status()
        return self.device_status
    
    def simulate_device_failure(self, device_name: str):
        """Simulate device disconnection"""
        if device_name in self.devices:
            if device_name == "arduino_main":
                self.devices[device_name].is_connected = False
            elif device_name == "camera":
                self.devices[device_name].is_active = False
            
            self.connection_log.append({
                "timestamp": datetime.now().isoformat(),
                "device": device_name,
                "event": "disconnected"
            })
            print(f"⚠️ Simulated {device_name} failure")
    
    def restore_device(self, device_name: str):
        """Restore device connection"""
        if device_name in self.devices:
            if device_name == "arduino_main":
                self.devices[device_name].is_connected = True
            elif device_name == "camera":
                self.devices[device_name].is_active = True
            
            self.connection_log.append({
                "timestamp": datetime.now().isoformat(),
                "device": device_name,
                "event": "reconnected"
            })
            print(f"✅ Restored {device_name} connection")


class VirtualGestureSimulator:
    """Virtual gesture simulator with GUI controls"""
    
    def __init__(self, iot_manager: IoTDeviceManager):
        self.iot_manager = iot_manager
        self.gesture_map = {
            "Hi": ("01000", "01000"),
            "Ambulance": ("01000", "00100"),
            "Fire": ("01100", "01100"),
            "Sick": ("00001", "00001"),
            "Water": ("10000", "10000"),
            "Up": ("01000", "00000"),
            "Down": ("00000", "01000"),
            "Danger": ("00001", "01000"),
            "Stop": ("00100", "00100"),
            "Wait": ("00010", "00010")
        }
        self.current_gesture = "Unknown"
        self.gesture_callbacks = []
    
    def add_gesture_callback(self, callback):
        """Add callback for gesture detection"""
        self.gesture_callbacks.append(callback)
    
    def simulate_gesture(self, gesture_name: str):
        """Simulate a specific gesture"""
        if gesture_name in self.gesture_map:
            self.current_gesture = gesture_name
            self.iot_manager.devices["camera"].current_gesture = gesture_name
            
            # Trigger callbacks
            for callback in self.gesture_callbacks:
                callback(gesture_name, self.gesture_map[gesture_name])
            
            print(f"👋 Simulated gesture: {gesture_name}")
        else:
            print(f"❌ Unknown gesture: {gesture_name}")
    
    def get_available_gestures(self) -> List[str]:
        """Get list of available gestures"""
        return list(self.gesture_map.keys())


# Global IoT manager instance
iot_manager = IoTDeviceManager()
gesture_simulator = VirtualGestureSimulator(iot_manager)

# Export mock classes for easy replacement
def get_mock_arduino(port='COM7'):
    """Get mock Arduino instance"""
    return iot_manager.devices["arduino_main"]

def get_mock_camera(source="http://10.170.105.110:81/stream"):
    """Get mock camera instance"""
    return iot_manager.devices["camera"]

# Patch functions for existing code
def patch_pyfirmata():
    """Patch pyfirmata to use mock Arduino"""
    import sys
    from types import ModuleType
    
    # Create mock pyfirmata module
    mock_pyfirmata = ModuleType('pyfirmata')
    mock_pyfirmata.Arduino = get_mock_arduino
    
    # Replace in sys.modules
    sys.modules['pyfirmata'] = mock_pyfirmata
    return mock_pyfirmata

def patch_cv2():
    """Patch cv2.VideoCapture to use mock camera"""
    import sys
    from types import ModuleType
    
    # This would require more complex patching
    # For now, we'll use the direct replacement approach
    pass


if __name__ == "__main__":
    print("🚀 IoT Hardware Simulation Layer Started")
    print("📊 Device Status:")
    status = iot_manager.get_device_status()
    for device, info in status.items():
        print(f"  {device}: {info}")
    
    print("\n👋 Available Gestures:")
    for gesture in gesture_simulator.get_available_gestures():
        print(f"  - {gesture}")
    
    # Test gesture simulation
    print("\n🧪 Testing gesture simulation...")
    gesture_simulator.simulate_gesture("Hi")
    gesture_simulator.simulate_gesture("Ambulance")
    
    print("\n✅ Simulation layer ready!")