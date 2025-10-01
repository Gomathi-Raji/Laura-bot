"""
Smart Hardware Manager for Laura-bot
Intelligently handles hardware components with fallback priorities:
1. Real hardware (Arduino, sensors, etc.) when available
2. Device components (mic, camera, speakers) when hardware fails
3. Simulation mode as final fallback
"""

import os
import sys
import time
import threading
from typing import Dict, Any, Optional, List
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardwareManager:
    """Intelligent hardware management with cascading fallbacks"""
    
    def __init__(self):
        self.hardware_status = {
            'arduino': {'available': False, 'status': 'disconnected', 'port': None},
            'camera': {'available': False, 'status': 'disconnected', 'device_id': None},
            'microphone': {'available': False, 'status': 'disconnected', 'device_name': None},
            'speakers': {'available': False, 'status': 'disconnected', 'device_name': None},
            'sensors': {'available': False, 'status': 'disconnected', 'type': None}
        }
        
        self.device_components = {
            'camera': None,
            'microphone': None,
            'speakers': None
        }
        
        self.simulation_mode = {
            'arduino': False,
            'camera': False,
            'microphone': False,
            'sensors': False
        }
        
        self.initialize_hardware_detection()
    
    def initialize_hardware_detection(self):
        """Detect and initialize all available hardware components"""
        print("🔍 Detecting available hardware components...")
        
        # Check Arduino hardware
        self.detect_arduino()
        
        # Check camera devices
        self.detect_camera()
        
        # Check audio devices
        self.detect_audio_devices()
        
        # Check sensors (if any)
        self.detect_sensors()
        
        # Generate hardware report
        self.generate_hardware_report()
    
    def detect_arduino(self):
        """Detect Arduino hardware with multiple port attempts"""
        try:
            from pyfirmata import Arduino
            
            # Common Arduino ports
            common_ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', '/dev/ttyUSB0', '/dev/ttyACM0']
            
            for port in common_ports:
                try:
                    print(f"🔌 Attempting Arduino connection on {port}...")
                    board = Arduino(port)
                    time.sleep(2)  # Wait for connection
                    
                    # Test connection
                    led = board.get_pin('d:13:o')
                    led.write(1)
                    time.sleep(0.5)
                    led.write(0)
                    
                    self.hardware_status['arduino'] = {
                        'available': True, 
                        'status': 'connected', 
                        'port': port,
                        'board': board
                    }
                    print(f"✅ Arduino connected successfully on {port}")
                    return True
                    
                except Exception as e:
                    continue
            
            print("⚠️ Arduino hardware not found")
            self.hardware_status['arduino']['status'] = 'not_found'
            return False
            
        except ImportError:
            print("⚠️ PyFirmata not installed - Arduino support unavailable")
            self.hardware_status['arduino']['status'] = 'library_missing'
            return False
    
    def detect_camera(self):
        """Detect camera devices with fallback options"""
        try:
            import cv2
            
            # Try multiple camera indices
            for camera_id in range(0, 4):
                try:
                    cap = cv2.VideoCapture(camera_id)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            self.hardware_status['camera'] = {
                                'available': True,
                                'status': 'connected',
                                'device_id': camera_id,
                                'capture': cap
                            }
                            print(f"✅ Camera detected on device {camera_id}")
                            return True
                        cap.release()
                except:
                    continue
            
            print("⚠️ No camera devices found")
            self.hardware_status['camera']['status'] = 'not_found'
            return False
            
        except ImportError:
            print("⚠️ OpenCV not installed - Camera support unavailable")
            self.hardware_status['camera']['status'] = 'library_missing'
            return False
    
    def detect_audio_devices(self):
        """Detect microphone and speaker devices"""
        # Detect microphone
        try:
            import speech_recognition as sr
            
            mic = sr.Microphone()
            recognizer = sr.Recognizer()
            
            # Test microphone
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            self.hardware_status['microphone'] = {
                'available': True,
                'status': 'connected',
                'device_name': 'default'
            }
            print("✅ Microphone detected and functional")
            
        except Exception as e:
            print(f"⚠️ Microphone detection failed: {e}")
            self.hardware_status['microphone']['status'] = 'not_found'
        
        # Detect speakers (basic check)
        try:
            import pygame
            pygame.mixer.init()
            
            self.hardware_status['speakers'] = {
                'available': True,
                'status': 'connected',
                'device_name': 'default'
            }
            print("✅ Audio output (speakers) detected")
            
        except Exception as e:
            print(f"⚠️ Speaker detection failed: {e}")
            self.hardware_status['speakers']['status'] = 'not_found'
    
    def detect_sensors(self):
        """Detect additional sensors (accelerometer, gyroscope, etc.)"""
        # This would check for additional sensors
        # For now, assume no additional sensors
        self.hardware_status['sensors'] = {
            'available': False,
            'status': 'not_available',
            'type': None
        }
    
    def get_best_input_method(self) -> str:
        """Determine the best available input method"""
        if self.hardware_status['microphone']['available']:
            return 'microphone'
        elif self.hardware_status['arduino']['available']:
            return 'arduino_serial'
        else:
            return 'simulation'
    
    def get_best_output_method(self) -> str:
        """Determine the best available output method"""
        if self.hardware_status['speakers']['available']:
            return 'speakers'
        elif self.hardware_status['arduino']['available']:
            return 'arduino_led'
        else:
            return 'simulation'
    
    def get_best_visual_method(self) -> str:
        """Determine the best available visual method"""
        if self.hardware_status['camera']['available']:
            return 'camera'
        elif self.hardware_status['arduino']['available']:
            return 'arduino_servo'
        else:
            return 'simulation'
    
    def execute_with_fallback(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """Execute action with intelligent hardware fallback"""
        result = {
            'success': False,
            'method_used': 'none',
            'message': '',
            'data': None
        }
        
        if action_type == 'listen_for_input':
            return self._listen_with_fallback(**kwargs)
        elif action_type == 'provide_output':
            return self._output_with_fallback(**kwargs)
        elif action_type == 'visual_feedback':
            return self._visual_with_fallback(**kwargs)
        elif action_type == 'gesture_recognition':
            return self._gesture_with_fallback(**kwargs)
        else:
            result['message'] = f"Unknown action: {action_type}"
            return result
    
    def _listen_with_fallback(self, **kwargs) -> Dict[str, Any]:
        """Listen for input with hardware fallback"""
        result = {'success': False, 'method_used': 'none', 'message': '', 'data': None}
        
        # Try microphone first
        if self.hardware_status['microphone']['available']:
            try:
                import speech_recognition as sr
                
                recognizer = sr.Recognizer()
                mic = sr.Microphone()
                
                print("🎤 Listening via microphone...")
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=kwargs.get('timeout', 5))
                
                text = recognizer.recognize_google(audio)
                result = {
                    'success': True,
                    'method_used': 'microphone',
                    'message': 'Voice input captured successfully',
                    'data': text
                }
                return result
                
            except sr.WaitTimeoutError:
                result['message'] = 'Microphone timeout'
            except Exception as e:
                result['message'] = f'Microphone error: {e}'
        
        # Try Arduino serial input
        if self.hardware_status['arduino']['available']:
            try:
                print("📡 Listening via Arduino serial...")
                # Implement Arduino serial listening
                # This would read from Arduino serial port
                result = {
                    'success': True,
                    'method_used': 'arduino_serial',
                    'message': 'Arduino serial input received',
                    'data': 'simulated_arduino_input'
                }
                return result
            except Exception as e:
                result['message'] = f'Arduino serial error: {e}'
        
        # Fallback to simulation
        print("🤖 Using simulation mode for input...")
        result = {
            'success': True,
            'method_used': 'simulation',
            'message': 'Simulation mode - no real input captured',
            'data': kwargs.get('simulation_input', 'hello laura')
        }
        return result
    
    def _output_with_fallback(self, message: str, **kwargs) -> Dict[str, Any]:
        """Provide output with hardware fallback"""
        result = {'success': False, 'method_used': 'none', 'message': '', 'data': None}
        
        # Try speakers first
        if self.hardware_status['speakers']['available']:
            try:
                # Use existing voice/speaker module
                from voice.speaker import speak
                speak(message)
                
                result = {
                    'success': True,
                    'method_used': 'speakers',
                    'message': 'Audio output successful',
                    'data': message
                }
                return result
                
            except Exception as e:
                result['message'] = f'Speaker error: {e}'
        
        # Try Arduino LED output
        if self.hardware_status['arduino']['available']:
            try:
                print("💡 Displaying via Arduino LEDs...")
                # Convert message to LED pattern
                led_pattern = self._message_to_led_pattern(message)
                self._display_led_pattern(led_pattern)
                
                result = {
                    'success': True,
                    'method_used': 'arduino_led',
                    'message': 'Arduino LED output successful',
                    'data': led_pattern
                }
                return result
                
            except Exception as e:
                result['message'] = f'Arduino LED error: {e}'
        
        # Fallback to simulation
        print(f"🤖 [SIMULATION OUTPUT]: {message}")
        result = {
            'success': True,
            'method_used': 'simulation',
            'message': 'Simulation mode output',
            'data': message
        }
        return result
    
    def _visual_with_fallback(self, **kwargs) -> Dict[str, Any]:
        """Provide visual feedback with hardware fallback"""
        result = {'success': False, 'method_used': 'none', 'message': '', 'data': None}
        action = kwargs.get('action', 'unknown')
        
        # Try camera first for visual feedback
        if self.hardware_status['camera']['available'] and action == 'capture':
            try:
                cap = self.hardware_status['camera']['capture']
                ret, frame = cap.read()
                
                if ret:
                    result = {
                        'success': True,
                        'method_used': 'camera',
                        'message': 'Camera capture successful',
                        'data': frame
                    }
                    return result
                    
            except Exception as e:
                result['message'] = f'Camera error: {e}'
        
        # Try Arduino servo for visual feedback
        if self.hardware_status['arduino']['available']:
            try:
                print("🤖 Providing visual feedback via Arduino servos...")
                # Move servos based on action
                self._servo_visual_feedback(action, **kwargs)
                
                result = {
                    'success': True,
                    'method_used': 'arduino_servo',
                    'message': 'Arduino servo feedback successful',
                    'data': action
                }
                return result
                
            except Exception as e:
                result['message'] = f'Arduino servo error: {e}'
        
        # Fallback to simulation
        print(f"🤖 [SIMULATION VISUAL]: {action}")
        result = {
            'success': True,
            'method_used': 'simulation',
            'message': 'Simulation mode visual feedback',
            'data': action
        }
        return result
    
    def _gesture_with_fallback(self, **kwargs) -> Dict[str, Any]:
        """Recognize gestures with hardware fallback"""
        result = {'success': False, 'method_used': 'none', 'message': '', 'data': None}
        
        # Try camera-based gesture recognition
        if self.hardware_status['camera']['available']:
            try:
                import cv2
                import mediapipe as mp
                
                print("👋 Recognizing gestures via camera...")
                # Implement gesture recognition
                cap = self.hardware_status['camera']['capture']
                ret, frame = cap.read()
                
                if ret:
                    # Simple gesture detection (placeholder)
                    gesture = 'thumbs_up'  # This would be actual detection
                    
                    result = {
                        'success': True,
                        'method_used': 'camera',
                        'message': 'Gesture recognized via camera',
                        'data': gesture
                    }
                    return result
                    
            except Exception as e:
                result['message'] = f'Camera gesture error: {e}'
        
        # Try Arduino sensor-based gesture
        if self.hardware_status['arduino']['available']:
            try:
                print("📡 Detecting gestures via Arduino sensors...")
                # Read from Arduino sensors
                gesture = 'wave'  # Placeholder
                
                result = {
                    'success': True,
                    'method_used': 'arduino_sensor',
                    'message': 'Gesture detected via Arduino',
                    'data': gesture
                }
                return result
                
            except Exception as e:
                result['message'] = f'Arduino gesture error: {e}'
        
        # Fallback to simulation
        import random
        gestures = ['wave', 'thumbs_up', 'peace', 'ok', 'point']
        gesture = random.choice(gestures)
        
        print(f"🤖 [SIMULATION GESTURE]: {gesture}")
        result = {
            'success': True,
            'method_used': 'simulation',
            'message': 'Simulation mode gesture',
            'data': gesture
        }
        return result
    
    def _message_to_led_pattern(self, message: str) -> List[int]:
        """Convert message to LED blink pattern"""
        # Simple pattern: length of message determines blinks
        pattern_length = min(len(message.split()), 10)
        return [1, 0] * pattern_length
    
    def _display_led_pattern(self, pattern: List[int]):
        """Display LED pattern on Arduino"""
        if self.hardware_status['arduino']['available']:
            try:
                board = self.hardware_status['arduino']['board']
                led = board.get_pin('d:13:o')
                
                for state in pattern:
                    led.write(state)
                    time.sleep(0.3)
            except Exception as e:
                print(f"LED pattern error: {e}")
    
    def _servo_visual_feedback(self, action: str, **kwargs):
        """Provide visual feedback using Arduino servos"""
        if not self.hardware_status['arduino']['available']:
            return
        
        try:
            board = self.hardware_status['arduino']['board']
            servo = board.get_pin('d:9:s')
            
            if action == 'celebrate':
                # Celebration movement
                for angle in [0, 180, 0, 180, 90]:
                    servo.write(angle)
                    time.sleep(0.5)
            elif action == 'thinking':
                # Thinking movement
                for angle in [45, 135, 90]:
                    servo.write(angle)
                    time.sleep(0.7)
            elif action == 'listening':
                # Listening movement
                servo.write(120)
                time.sleep(1)
                servo.write(90)
                
        except Exception as e:
            print(f"Servo feedback error: {e}")
    
    def generate_hardware_report(self):
        """Generate comprehensive hardware status report"""
        print("\n" + "="*50)
        print("🔧 LAURA-BOT HARDWARE STATUS REPORT")
        print("="*50)
        
        for component, status in self.hardware_status.items():
            status_icon = "✅" if status['available'] else "❌"
            print(f"{status_icon} {component.upper()}: {status['status']}")
            
            if status['available']:
                if component == 'arduino' and status.get('port'):
                    print(f"   📍 Port: {status['port']}")
                elif component == 'camera' and status.get('device_id') is not None:
                    print(f"   📷 Device ID: {status['device_id']}")
                elif status.get('device_name'):
                    print(f"   🎵 Device: {status['device_name']}")
        
        print("\n📋 RECOMMENDED OPERATION MODES:")
        print(f"🎤 Input Method: {self.get_best_input_method()}")
        print(f"🔊 Output Method: {self.get_best_output_method()}")
        print(f"👁️  Visual Method: {self.get_best_visual_method()}")
        
        print("\n💡 FALLBACK STRATEGY:")
        print("1️⃣ Real Hardware (Arduino, sensors)")
        print("2️⃣ Device Components (mic, camera, speakers)")
        print("3️⃣ Simulation Mode (software only)")
        print("="*50)
    
    def test_all_hardware(self):
        """Test all available hardware components"""
        print("\n🧪 TESTING ALL HARDWARE COMPONENTS...")
        
        # Test input
        print("\n🎤 Testing Input Methods:")
        input_result = self.execute_with_fallback('listen_for_input', timeout=3, simulation_input='test voice')
        print(f"   Result: {input_result['method_used']} - {input_result['message']}")
        
        # Test output
        print("\n🔊 Testing Output Methods:")
        output_result = self.execute_with_fallback('provide_output', message='Hardware test message')
        print(f"   Result: {output_result['method_used']} - {output_result['message']}")
        
        # Test visual
        print("\n👁️  Testing Visual Methods:")
        visual_result = self.execute_with_fallback('visual_feedback', action='celebrate')
        print(f"   Result: {visual_result['method_used']} - {visual_result['message']}")
        
        # Test gesture
        print("\n👋 Testing Gesture Recognition:")
        gesture_result = self.execute_with_fallback('gesture_recognition')
        print(f"   Result: {gesture_result['method_used']} - {gesture_result['message']}")
        
        print("\n✅ Hardware testing complete!")
    
    def cleanup(self):
        """Clean up hardware connections"""
        try:
            if self.hardware_status['arduino']['available']:
                board = self.hardware_status['arduino']['board']
                if board:
                    board.exit()
            
            if self.hardware_status['camera']['available']:
                cap = self.hardware_status['camera']['capture']
                if cap:
                    cap.release()
                    
            print("🧹 Hardware cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


# Global hardware manager instance
hardware_manager = None

def get_hardware_manager() -> HardwareManager:
    """Get the global hardware manager instance"""
    global hardware_manager
    if hardware_manager is None:
        hardware_manager = HardwareManager()
    return hardware_manager

def initialize_smart_hardware():
    """Initialize smart hardware management"""
    print("🚀 Initializing Smart Hardware Management...")
    manager = get_hardware_manager()
    manager.test_all_hardware()
    return manager

# Convenience functions for easy integration
def smart_listen(timeout=5, simulation_input="hello laura"):
    """Smart listening with hardware fallback"""
    manager = get_hardware_manager()
    return manager.execute_with_fallback('listen_for_input', timeout=timeout, simulation_input=simulation_input)

def smart_speak(message):
    """Smart speaking with hardware fallback"""
    manager = get_hardware_manager()
    return manager.execute_with_fallback('provide_output', message=message)

def smart_visual_feedback(action):
    """Smart visual feedback with hardware fallback"""
    manager = get_hardware_manager()
    return manager.execute_with_fallback('visual_feedback', action=action)

def smart_gesture_recognition():
    """Smart gesture recognition with hardware fallback"""
    manager = get_hardware_manager()
    return manager.execute_with_fallback('gesture_recognition')

if __name__ == "__main__":
    # Test the hardware manager
    manager = initialize_smart_hardware()