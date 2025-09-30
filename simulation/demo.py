"""
IoT Simulation Demo
==================
Demonstration script showcasing all simulation capabilities.
"""

import time
import random
import threading
from datetime import datetime

# Import simulation modules
from iot_hardware_sim import iot_manager, gesture_simulator
from sensor_simulation import sensor_simulator, data_logger


def demo_header():
    """Display demo header"""
    print("=" * 60)
    print("🤖 LAURA-BOT IoT SIMULATION DEMONSTRATION")
    print("=" * 60)
    print("🎯 This demo showcases virtual IoT capabilities")
    print("⏱️  Duration: ~2 minutes")
    print("=" * 60)
    print()


def demo_hardware_simulation():
    """Demonstrate hardware simulation"""
    print("🔌 HARDWARE SIMULATION DEMO")
    print("-" * 30)
    
    # Arduino simulation
    print("📡 Testing mock Arduino...")
    arduino = iot_manager.devices["arduino_main"]
    print(f"   ✅ Arduino connected to {arduino.port}")
    
    # Servo control simulation
    print("🤖 Testing servo control...")
    servo_pin = arduino.digital[9]
    servo_pin.mode = 4  # Servo mode
    
    for angle in [0, 90, 180, 90]:
        servo_pin.write(angle)
        print(f"   🔄 Servo moved to {angle}°")
        time.sleep(0.5)
    
    # Camera simulation
    print("📹 Testing virtual camera...")
    camera = iot_manager.devices["camera"]
    ret, frame = camera.read()
    print(f"   ✅ Camera active: {camera.is_active}")
    print(f"   📸 Frame captured: {frame}")
    print()


def demo_sensor_network():
    """Demonstrate sensor network"""
    print("🌡️ SENSOR NETWORK DEMO")
    print("-" * 25)
    
    # Start sensor simulation
    print("🚀 Starting sensor network...")
    sensor_simulator.start_simulation()
    data_logger.start_logging()
    
    # Wait for data generation
    time.sleep(3)
    
    # Display current readings
    readings = sensor_simulator.get_current_readings()
    print("📊 Current sensor readings:")
    
    for reading in readings[:5]:  # Show first 5 sensors
        status_emoji = {"normal": "✅", "warning": "⚠️", "critical": "🚨"}
        emoji = status_emoji.get(reading.status, "❓")
        print(f"   {emoji} {reading.sensor_type:15} ({reading.location:12}): {reading.value:6.1f} {reading.unit}")
    
    # Show statistics
    stats = sensor_simulator.get_statistics()
    print(f"\n📈 Network statistics:")
    print(f"   • Active sensors: {stats['active_sensors']}/{stats['total_sensors']}")
    print(f"   • Total readings: {stats['total_readings']}")
    print(f"   • Alerts: {stats['warning_alerts']} warnings, {stats['critical_alerts']} critical")
    print()


def demo_gesture_simulation():
    """Demonstrate gesture simulation"""
    print("👋 GESTURE SIMULATION DEMO")
    print("-" * 27)
    
    gestures_to_demo = ["Hi", "Ambulance", "Fire", "Water", "Stop"]
    
    print("🎯 Simulating gestures...")
    for gesture in gestures_to_demo:
        gesture_simulator.simulate_gesture(gesture)
        left, right = gesture_simulator.gesture_map[gesture]
        print(f"   👐 {gesture:10} | Left: {left} | Right: {right}")
        time.sleep(1)
    
    print("✅ Gesture simulation complete")
    print()


def demo_device_management():
    """Demonstrate device management"""
    print("🔧 DEVICE MANAGEMENT DEMO")
    print("-" * 26)
    
    # Show initial status
    print("📊 Initial device status:")
    status = iot_manager.get_device_status()
    for device, info in status.items():
        if device == "arduino_main":
            print(f"   🔌 Arduino: {'Connected' if info['connected'] else 'Disconnected'}")
        elif device == "camera":
            print(f"   📹 Camera: {'Active' if info['active'] else 'Inactive'}")
    
    # Simulate device failure
    print("\n⚠️ Simulating device failure...")
    iot_manager.simulate_device_failure("arduino_main")
    time.sleep(1)
    
    status = iot_manager.get_device_status()
    arduino_status = "Connected" if status["arduino_main"]["connected"] else "Disconnected"
    print(f"   🔌 Arduino: {arduino_status}")
    
    # Restore device
    print("\n🔄 Restoring device...")
    iot_manager.restore_device("arduino_main")
    time.sleep(1)
    
    status = iot_manager.get_device_status()
    arduino_status = "Connected" if status["arduino_main"]["connected"] else "Disconnected"
    print(f"   🔌 Arduino: {arduino_status}")
    print()


def demo_alerts_system():
    """Demonstrate alerts system"""
    print("🚨 ALERTS SYSTEM DEMO")
    print("-" * 22)
    
    # Simulate high temperature alert
    print("🌡️ Simulating temperature alert...")
    temp_sensor = sensor_simulator.sensors["temp_001"]
    original_temp = temp_sensor["current_value"]
    
    # Force high temperature
    temp_sensor["current_value"] = 38.0  # Critical threshold
    time.sleep(2)  # Wait for alert generation
    
    # Check for alerts
    alerts = sensor_simulator.get_alerts(limit=3)
    if alerts:
        print("📋 Recent alerts:")
        for alert in alerts[-2:]:
            status_emoji = {"warning": "⚠️", "critical": "🚨"}
            emoji = status_emoji.get(alert["status"], "ℹ️")
            timestamp = datetime.fromisoformat(alert["timestamp"]).strftime("%H:%M:%S")
            print(f"   {emoji} [{timestamp}] {alert['message']}")
    
    # Restore normal temperature
    temp_sensor["current_value"] = original_temp
    print("✅ Temperature restored to normal")
    print()


def demo_dashboard_info():
    """Show dashboard information"""
    print("📊 IoT DASHBOARD INFO")
    print("-" * 21)
    print("🌐 Web dashboard available at: http://localhost:8501")
    print("🎛️ Features:")
    print("   • Real-time sensor monitoring")
    print("   • Interactive device controls")
    print("   • Data visualization charts")
    print("   • Alert management system")
    print("   • Gesture simulation controls")
    print("   • Data export capabilities")
    print()
    print("💡 To start dashboard: streamlit run simulation/iot_dashboard.py")
    print()


def demo_cleanup():
    """Clean up demo resources"""
    print("🧹 CLEANUP")
    print("-" * 10)
    print("⏹️ Stopping sensor simulation...")
    sensor_simulator.stop_simulation()
    data_logger.stop_logging()
    print("✅ Demo cleanup complete")
    print()


def run_full_demo():
    """Run the complete demonstration"""
    demo_header()
    
    try:
        # Run all demo sections
        demo_hardware_simulation()
        demo_sensor_network()
        demo_gesture_simulation()
        demo_device_management()
        demo_alerts_system()
        demo_dashboard_info()
        
        # Summary
        print("🎉 DEMO COMPLETE!")
        print("-" * 16)
        print("✅ All simulation components demonstrated successfully")
        print("🚀 Ready for full IoT simulation deployment!")
        print()
        print("Next steps:")
        print("1. Run 'python simulation/launcher.py' for full GUI")
        print("2. Start dashboard with 'streamlit run simulation/iot_dashboard.py'")
        print("3. Launch gesture panel with 'python simulation/gesture_simulator.py'")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
    finally:
        demo_cleanup()


def run_quick_demo():
    """Run a quick 30-second demo"""
    print("⚡ QUICK DEMO (30 seconds)")
    print("-" * 25)
    
    # Quick sensor test
    sensor_simulator.start_simulation()
    time.sleep(2)
    
    readings = sensor_simulator.get_current_readings()
    print(f"📊 {len(readings)} sensors active")
    
    # Quick gesture test
    gesture_simulator.simulate_gesture("Hi")
    print("👋 Gesture simulation: Hi")
    
    # Quick device test
    status = iot_manager.get_device_status()
    arduino_connected = status["arduino_main"]["connected"]
    camera_active = status["camera"]["active"]
    print(f"🔌 Arduino: {'✅' if arduino_connected else '❌'}")
    print(f"📹 Camera: {'✅' if camera_active else '❌'}")
    
    sensor_simulator.stop_simulation()
    print("✅ Quick demo complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_demo()
    else:
        run_full_demo()