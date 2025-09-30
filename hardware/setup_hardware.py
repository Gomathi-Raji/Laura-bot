#!/usr/bin/env python3
"""
Laura-bot Hardware Setup and Configuration Tool
Helps users set up and test their hardware connections
"""

import os
import sys
import json
import time
import serial
import serial.tools.list_ports
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🤖 LAURA-BOT HARDWARE SETUP")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking hardware dependencies...")
    
    missing_deps = []
    optional_deps = []
    
    # Required dependencies
    required = {
        'serial': 'pyserial',
        'pyfirmata': 'pyfirmata',
        'cv2': 'opencv-python',
        'speech_recognition': 'SpeechRecognition',
        'pyttsx3': 'pyttsx3'
    }
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Not installed")
            missing_deps.append(package)
    
    # Optional dependencies
    optional = {
        'mediapipe': 'mediapipe',
        'tensorflow': 'tensorflow',
        'RPi.GPIO': 'RPi.GPIO'
    }
    
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"   ✅ {package} (optional)")
        except ImportError:
            print(f"   ⚠️ {package} (optional) - Not installed")
            optional_deps.append(package)
    
    print()
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        print(f"   Install with: pip install {' '.join(missing_deps)}")
        print("   Or use: pip install -r hardware_requirements.txt")
        return False
    
    if optional_deps:
        print("ℹ️ Optional dependencies not installed:")
        print(f"   Install with: pip install {' '.join(optional_deps)}")
    
    print("✅ All required dependencies are installed!")
    return True

def scan_serial_ports():
    """Scan and list available serial ports"""
    print("🔍 Scanning for serial ports...")
    
    ports = serial.tools.list_ports.comports()
    available_ports = []
    
    if not ports:
        print("   ❌ No serial ports found")
        return available_ports
    
    for port in ports:
        print(f"   📍 {port.device} - {port.description}")
        if 'Arduino' in port.description or 'USB' in port.description:
            print(f"      🎯 Potential Arduino/Robot port")
        available_ports.append(port.device)
    
    return available_ports

def test_arduino_connection(port):
    """Test Arduino connection"""
    print(f"🔌 Testing Arduino connection on {port}...")
    
    try:
        from pyfirmata import Arduino, util
        
        print("   🔄 Connecting to Arduino...")
        board = Arduino(port)
        
        print("   🔄 Setting up pins...")
        led = board.get_pin('d:13:o')  # Built-in LED
        
        print("   🔄 Testing LED blink...")
        for i in range(3):
            led.write(1)
            time.sleep(0.5)
            led.write(0)
            time.sleep(0.5)
        
        board.exit()
        print("   ✅ Arduino connection successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ Arduino connection failed: {e}")
        return False

def test_serial_communication(port):
    """Test basic serial communication"""
    print(f"📡 Testing serial communication on {port}...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        
        print("   🔄 Sending test message...")
        test_message = '{"type":"ping"}\n'
        ser.write(test_message.encode())
        
        print("   🔄 Waiting for response...")
        response = ser.readline().decode().strip()
        
        ser.close()
        
        if response:
            print(f"   ✅ Received response: {response}")
            return True
        else:
            print("   ⚠️ No response received (this may be normal)")
            return False
            
    except Exception as e:
        print(f"   ❌ Serial communication failed: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    print("📷 Testing camera...")
    
    try:
        import cv2
        
        print("   🔄 Opening camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("   ❌ Failed to open camera")
            return False
        
        print("   🔄 Capturing test frame...")
        ret, frame = cap.read()
        
        if ret:
            height, width = frame.shape[:2]
            print(f"   ✅ Camera working! Resolution: {width}x{height}")
        else:
            print("   ❌ Failed to capture frame")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
        return False

def test_speech():
    """Test speech synthesis and recognition"""
    print("🎤 Testing speech system...")
    
    # Test speech synthesis
    try:
        import pyttsx3
        
        print("   🔄 Testing text-to-speech...")
        engine = pyttsx3.init()
        engine.say("Laura-bot hardware test")
        engine.runAndWait()
        engine.stop()
        print("   ✅ Text-to-speech working!")
        
    except Exception as e:
        print(f"   ❌ Text-to-speech failed: {e}")
        return False
    
    # Test speech recognition
    try:
        import speech_recognition as sr
        
        print("   🔄 Testing speech recognition...")
        r = sr.Recognizer()
        
        # Test microphone access
        with sr.Microphone() as source:
            print("   🎯 Microphone detected!")
            r.adjust_for_ambient_noise(source, duration=0.5)
        
        print("   ✅ Speech recognition ready!")
        return True
        
    except Exception as e:
        print(f"   ❌ Speech recognition failed: {e}")
        return False

def create_hardware_config():
    """Create hardware configuration file"""
    print("⚙️ Creating hardware configuration...")
    
    config = {
        "arduino": {
            "port": "COM7",
            "baudrate": 9600,
            "timeout": 1.0
        },
        "serial": {
            "port": "COM3", 
            "baudrate": 115200,
            "timeout": 0.5
        },
        "camera": {
            "device_id": 0,
            "width": 640,
            "height": 480,
            "fps": 30
        },
        "speech": {
            "recognition_timeout": 5.0,
            "synthesis_rate": 200,
            "synthesis_volume": 0.8
        },
        "robot": {
            "ip_address": "192.168.1.100",
            "port": 8080,
            "protocol": "tcp"
        },
        "sensors": {
            "update_rate": 0.1,
            "buffer_size": 100
        }
    }
    
    # Ask user for port configuration
    ports = scan_serial_ports()
    
    if ports:
        print("\n📝 Port Configuration:")
        print("Available ports:")
        for i, port in enumerate(ports):
            print(f"   {i+1}. {port}")
        
        # Arduino port
        while True:
            try:
                choice = input(f"\nSelect Arduino port (1-{len(ports)}) or press Enter for default: ").strip()
                if not choice:
                    break
                
                idx = int(choice) - 1
                if 0 <= idx < len(ports):
                    config["arduino"]["port"] = ports[idx]
                    print(f"   ✅ Arduino port set to: {ports[idx]}")
                    break
                else:
                    print("   ❌ Invalid selection")
            except ValueError:
                print("   ❌ Please enter a number")
        
        # Robot communication port
        while True:
            try:
                choice = input(f"\nSelect robot communication port (1-{len(ports)}) or press Enter for default: ").strip()
                if not choice:
                    break
                
                idx = int(choice) - 1
                if 0 <= idx < len(ports):
                    config["serial"]["port"] = ports[idx]
                    print(f"   ✅ Robot port set to: {ports[idx]}")
                    break
                else:
                    print("   ❌ Invalid selection")
            except ValueError:
                print("   ❌ Please enter a number")
    
    # Save configuration
    config_path = Path(__file__).parent / "hardware_config.json"
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"   ✅ Configuration saved to: {config_path}")
    return config

def run_full_test():
    """Run comprehensive hardware test"""
    print("🧪 Running comprehensive hardware test...\n")
    
    results = {
        "dependencies": False,
        "arduino": False,
        "serial": False,
        "camera": False,
        "speech": False
    }
    
    # Check dependencies
    results["dependencies"] = check_dependencies()
    print()
    
    if not results["dependencies"]:
        print("❌ Cannot proceed without required dependencies")
        return results
    
    # Scan ports
    ports = scan_serial_ports()
    print()
    
    # Test Arduino connection
    if ports:
        for port in ports:
            if 'Arduino' in str(port) or 'USB' in str(port):
                results["arduino"] = test_arduino_connection(port)
                if results["arduino"]:
                    break
        
        if not results["arduino"]:
            # Try first available port
            results["arduino"] = test_arduino_connection(ports[0])
        
        print()
        
        # Test serial communication
        for port in ports:
            results["serial"] = test_serial_communication(port)
            if results["serial"]:
                break
        
        print()
    
    # Test camera
    results["camera"] = test_camera()
    print()
    
    # Test speech
    results["speech"] = test_speech()
    print()
    
    return results

def print_results(results):
    """Print test results summary"""
    print("📊 HARDWARE TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component.capitalize()}: {'PASS' if status else 'FAIL'}")
        if status:
            passed += 1
    
    print("=" * 40)
    print(f"Overall: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 All hardware components are working perfectly!")
        print("🚀 Your Laura-bot is ready for action!")
    elif passed >= total // 2:
        print("⚠️ Most components are working. Check failed components.")
        print("💡 You can still use Laura-bot with limited functionality.")
    else:
        print("❌ Multiple hardware issues detected.")
        print("🔧 Please check connections and install missing dependencies.")
    
    print()
    print("💡 Tips:")
    print("   • Make sure your Arduino is connected via USB")
    print("   • Check that drivers are installed for your hardware")
    print("   • Ensure no other programs are using the serial ports")
    print("   • For speech features, check your microphone permissions")

def main():
    """Main setup function"""
    print_header()
    
    print("Welcome to Laura-bot Hardware Setup!")
    print("This tool will help you configure and test your hardware connections.\n")
    
    while True:
        print("Choose an option:")
        print("1. Run full hardware test")
        print("2. Check dependencies only")
        print("3. Scan serial ports")
        print("4. Test specific component")
        print("5. Create hardware configuration")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print()
            results = run_full_test()
            print_results(results)
            
        elif choice == '2':
            print()
            check_dependencies()
            
        elif choice == '3':
            print()
            scan_serial_ports()
            
        elif choice == '4':
            print("\nChoose component to test:")
            print("1. Camera")
            print("2. Speech system")
            print("3. Arduino (requires port selection)")
            
            comp_choice = input("Enter choice (1-3): ").strip()
            print()
            
            if comp_choice == '1':
                test_camera()
            elif comp_choice == '2':
                test_speech()
            elif comp_choice == '3':
                ports = scan_serial_ports()
                if ports:
                    port_choice = input(f"Enter port to test: ").strip()
                    test_arduino_connection(port_choice)
                
        elif choice == '5':
            print()
            create_hardware_config()
            
        elif choice == '6':
            print("\n👋 Goodbye! Happy robot building!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        print("Please report this issue if it persists.")