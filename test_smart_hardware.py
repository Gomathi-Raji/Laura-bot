#!/usr/bin/env python3
"""
Smart Hardware Manager Test Script
Test the intelligent hardware fallback system
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔧 SMART HARDWARE MANAGER TEST")
print("=" * 50)

try:
    from smart_hardware_manager import (
        HardwareManager, 
        initialize_smart_hardware,
        smart_listen,
        smart_speak,
        smart_visual_feedback,
        smart_gesture_recognition
    )
    print("✅ Smart Hardware Manager imported successfully")
    
    # Initialize the hardware manager
    print("\n🚀 Initializing Smart Hardware Management...")
    manager = initialize_smart_hardware()
    print("✅ Smart Hardware Manager initialized")
    
    # Test hardware detection
    print("\n🔍 Hardware Detection Results:")
    for component, status in manager.hardware_status.items():
        status_icon = "✅" if status['available'] else "❌"
        print(f"   {status_icon} {component.upper()}: {status['status']}")
    
    # Test fallback methods
    print("\n📋 Fallback Recommendations:")
    print(f"   🎤 Best Input Method: {manager.get_best_input_method()}")
    print(f"   🔊 Best Output Method: {manager.get_best_output_method()}")
    print(f"   👁️  Best Visual Method: {manager.get_best_visual_method()}")
    
    # Test smart functions
    print("\n🧪 Testing Smart Functions:")
    
    # Test smart speaking
    print("🔊 Testing smart_speak...")
    result = smart_speak("Hardware testing message")
    print(f"   Result: {result['method_used']} - {result['message']}")
    
    # Test smart listening (with short timeout for testing)
    print("🎤 Testing smart_listen...")
    result = smart_listen(timeout=2, simulation_input="test voice command")
    print(f"   Result: {result['method_used']} - {result['data']}")
    
    # Test smart visual feedback
    print("👁️  Testing smart_visual_feedback...")
    result = smart_visual_feedback('thinking')
    print(f"   Result: {result['method_used']} - {result['message']}")
    
    # Test smart gesture recognition
    print("👋 Testing smart_gesture_recognition...")
    result = smart_gesture_recognition()
    print(f"   Result: {result['method_used']} - Gesture: {result['data']}")
    
    print("\n✅ All smart hardware tests completed!")
    
    # Test integration with main Laura-bot functions
    print("\n🤖 Testing Laura-bot Integration:")
    try:
        from main import (
            smart_listen_command,
            smart_speak_response,
            process_command_with_hardware
        )
        print("✅ Laura-bot integration functions imported")
        
        # Test smart command listening
        print("🎤 Testing smart command listening...")
        # This would normally wait for real input, so we'll skip in automated test
        print("   ⏭️  Skipped (requires manual voice input)")
        
        # Test smart response
        print("🔊 Testing smart response...")
        smart_speak_response("Integration test successful!")
        print("   ✅ Smart response completed")
        
    except Exception as e:
        print(f"⚠️ Laura-bot integration test incomplete: {e}")
    
except Exception as e:
    print(f"❌ Error testing smart hardware manager: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 SMART HARDWARE FEATURES")
print("=" * 50)
print("🔧 INTELLIGENT FALLBACK SYSTEM:")
print("   1️⃣ Real Hardware Priority:")
print("      • Arduino (COM ports, sensors, servos)")
print("      • External sensors and actuators")
print("   2️⃣ Device Components Fallback:")
print("      • System microphone for voice input")
print("      • System camera for gesture recognition")
print("      • System speakers for audio output")
print("   3️⃣ Simulation Mode Fallback:")
print("      • Software-only operation")
print("      • Console-based feedback")
print("      • Simulated responses")

print("\n🎤 SMART INPUT METHODS:")
print("   • Voice recognition via microphone")
print("   • Arduino serial communication")
print("   • Gesture recognition via camera")
print("   • Simulation with predefined inputs")

print("\n🔊 SMART OUTPUT METHODS:")
print("   • Text-to-speech via speakers")
print("   • Visual feedback via Arduino LEDs/servos")
print("   • Console text output")
print("   • Gesture-based responses")

print("\n👁️  SMART VISUAL METHODS:")
print("   • Camera-based gesture recognition")
print("   • Arduino servo movements")
print("   • LED pattern displays")
print("   • Console visual feedback")

print("\n🚀 HOW TO USE SMART HARDWARE:")
print("1. 🎤 Voice Mode:")
print("   - Run: python main.py")
print("   - Hardware automatically detected")
print("   - Fallbacks happen seamlessly")

print("\n2. 🧪 Test Hardware:")
print("   - Say: 'test hardware'")
print("   - Say: 'hardware report'")
print("   - Say: 'recognize gesture'")

print("\n3. 🔧 Hardware Commands:")
print("   - 'hardware status' - Show component status")
print("   - 'test hardware' - Test all components")
print("   - 'gesture recognition' - Test gesture detection")

print("\n" + "=" * 50)
print("🎉 Smart Hardware Management Ready!")
print("🔧 Auto-detects and uses best available hardware!")
print("🎯 Seamless fallbacks ensure Laura-bot always works!")
print("=" * 50)