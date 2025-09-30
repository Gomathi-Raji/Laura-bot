"""
Laura-bot IoT Simulation Package
===============================

Complete simulation environment for testing IoT features without physical hardware.

Components:
- Hardware simulation (Arduino, camera, sensors)
- Gesture recognition simulation
- Real-time sensor data generation
- Web-based IoT dashboard
- Device management and failure simulation

Usage:
    from simulation import iot_manager, gesture_simulator, sensor_simulator
    
    # Start simulation
    sensor_simulator.start_simulation()
    
    # Trigger gesture
    gesture_simulator.simulate_gesture("Hi")
    
    # Get device status
    status = iot_manager.get_device_status()

Quick start:
    python simulation/launcher.py      # GUI launcher
    python simulation/demo.py          # Full demonstration
    python simulation/demo.py quick    # Quick test

Web interfaces:
    streamlit run simulation/iot_dashboard.py     # IoT dashboard
    python simulation/gesture_simulator.py        # Gesture panel
"""

__version__ = "1.0.0"
__author__ = "Laura-bot Development Team"

# Import main simulation components
try:
    from .iot_hardware_sim import iot_manager, gesture_simulator, get_mock_arduino, get_mock_camera
    from .sensor_simulation import sensor_simulator, data_logger
    
    __all__ = [
        'iot_manager',
        'gesture_simulator', 
        'sensor_simulator',
        'data_logger',
        'get_mock_arduino',
        'get_mock_camera'
    ]
    
except ImportError as e:
    print(f"⚠️ Warning: Could not import simulation components: {e}")
    print("Some simulation features may not be available.")
    __all__ = []

# Simulation status
SIMULATION_READY = len(__all__) > 0

if SIMULATION_READY:
    print("🤖 Laura-bot IoT Simulation package loaded successfully")
else:
    print("❌ Laura-bot IoT Simulation package failed to load")