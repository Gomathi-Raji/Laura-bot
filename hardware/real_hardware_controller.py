"""
Real Hardware Integration Controller for Laura-bot
Handles connection to actual chatbot/robot hardware components
Provides unified interface for sensors, actuators, and communication
"""

import time
import threading
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
import serial
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardware component imports with fallbacks
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("PySerial not available - Serial communication disabled")

try:
    from pyfirmata import Arduino, util
    ARDUINO_AVAILABLE = True
except ImportError:
    ARDUINO_AVAILABLE = False
    logger.warning("PyFirmata not available - Arduino support disabled")

try:
    import cv2
    import mediapipe as mp
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    logger.warning("Camera/MediaPipe not available - Vision features disabled")

try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    logger.warning("Speech libraries not available - Voice features disabled")

class RealHardwareController:
    """Main controller for real chatbot/robot hardware integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.is_connected = False
        self.hardware_status = {}
        self.sensor_data = {}
        self.callbacks = {}
        self.running = False
        
        # Hardware components
        self.arduino = None
        self.serial_connection = None
        self.camera = None
        self.microphone = None
        self.speaker = None
        
        # Threading
        self.sensor_thread = None
        self.communication_thread = None
        self.heartbeat_thread = None
        
        # Initialize components
        self._initialize_hardware()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default hardware configuration"""
        return {
            'arduino': {
                'port': 'COM7',  # Default Arduino port for Windows
                'baudrate': 9600,
                'timeout': 1.0
            },
            'serial': {
                'port': 'COM3',  # Default serial port for robot communication
                'baudrate': 115200,
                'timeout': 0.5
            },
            'camera': {
                'device_id': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'speech': {
                'recognition_timeout': 5.0,
                'synthesis_rate': 200,
                'synthesis_volume': 0.8
            },
            'robot': {
                'ip_address': '192.168.1.100',  # Default robot IP
                'port': 8080,
                'protocol': 'tcp'
            },
            'sensors': {
                'update_rate': 0.1,  # 10Hz update rate
                'buffer_size': 100
            }
        }
    
    def _initialize_hardware(self):
        """Initialize all hardware components"""
        logger.info("🤖 Initializing hardware components...")
        
        # Initialize Arduino
        if self._init_arduino():
            self.hardware_status['arduino'] = 'connected'
        else:
            self.hardware_status['arduino'] = 'disconnected'
        
        # Initialize Serial Communication
        if self._init_serial():
            self.hardware_status['serial'] = 'connected'
        else:
            self.hardware_status['serial'] = 'disconnected'
        
        # Initialize Camera
        if self._init_camera():
            self.hardware_status['camera'] = 'connected'
        else:
            self.hardware_status['camera'] = 'disconnected'
        
        # Initialize Speech System
        if self._init_speech():
            self.hardware_status['speech'] = 'connected'
        else:
            self.hardware_status['speech'] = 'disconnected'
        
        # Check overall connection status
        self.is_connected = any(status == 'connected' for status in self.hardware_status.values())
        
        if self.is_connected:
            logger.info("✅ Hardware initialization complete")
        else:
            logger.warning("⚠️ No hardware components connected - running in simulation mode")
    
    def _init_arduino(self) -> bool:
        """Initialize Arduino connection"""
        if not ARDUINO_AVAILABLE:
            return False
        
        try:
            port = self.config['arduino']['port']
            logger.info(f"🔌 Connecting to Arduino on {port}...")
            
            self.arduino = Arduino(port)
            
            # Setup pins
            self.servo_pins = {
                'head_pan': self.arduino.get_pin('d:9:s'),
                'head_tilt': self.arduino.get_pin('d:10:s'),
                'arm_left': self.arduino.get_pin('d:6:s'),
                'arm_right': self.arduino.get_pin('d:5:s')
            }
            
            self.digital_pins = {
                'led_status': self.arduino.get_pin('d:13:o'),
                'led_eyes': self.arduino.get_pin('d:12:o'),
                'buzzer': self.arduino.get_pin('d:11:o')
            }
            
            self.analog_pins = {
                'distance_sensor': self.arduino.get_pin('a:0:i'),
                'light_sensor': self.arduino.get_pin('a:1:i'),
                'microphone': self.arduino.get_pin('a:2:i')
            }
            
            # Start iterator for reading analog data
            self.iterator = util.Iterator(self.arduino)
            self.iterator.start()
            
            # Test connection
            self.digital_pins['led_status'].write(1)
            time.sleep(0.1)
            self.digital_pins['led_status'].write(0)
            
            logger.info("✅ Arduino connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Arduino connection failed: {e}")
            return False
    
    def _init_serial(self) -> bool:
        """Initialize serial communication with robot"""
        if not SERIAL_AVAILABLE:
            return False
        
        try:
            port = self.config['serial']['port']
            baudrate = self.config['serial']['baudrate']
            
            logger.info(f"📡 Connecting to robot via serial {port}@{baudrate}...")
            
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=self.config['serial']['timeout']
            )
            
            # Test communication
            self.serial_connection.write(b'{"type":"ping"}\n')
            response = self.serial_connection.readline().decode().strip()
            
            if response:
                logger.info("✅ Serial communication established")
                return True
            else:
                logger.warning("⚠️ No response from robot")
                return False
                
        except Exception as e:
            logger.error(f"❌ Serial connection failed: {e}")
            return False
    
    def _init_camera(self) -> bool:
        """Initialize camera for vision processing"""
        if not CAMERA_AVAILABLE:
            return False
        
        try:
            device_id = self.config['camera']['device_id']
            logger.info(f"📷 Initializing camera (device {device_id})...")
            
            self.camera = cv2.VideoCapture(device_id)
            
            if not self.camera.isOpened():
                logger.error("❌ Failed to open camera")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
            self.camera.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])
            
            # Initialize MediaPipe for gesture recognition
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            
            logger.info("✅ Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Camera initialization failed: {e}")
            return False
    
    def _init_speech(self) -> bool:
        """Initialize speech recognition and synthesis"""
        if not SPEECH_AVAILABLE:
            return False
        
        try:
            logger.info("🎤 Initializing speech system...")
            
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Initialize text-to-speech
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.config['speech']['synthesis_rate'])
            self.tts_engine.setProperty('volume', self.config['speech']['synthesis_volume'])
            
            # Test microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("✅ Speech system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Speech initialization failed: {e}")
            return False
    
    def start_monitoring(self):
        """Start hardware monitoring threads"""
        if self.running:
            return
        
        self.running = True
        
        # Start sensor monitoring thread
        if any(status == 'connected' for status in self.hardware_status.values()):
            self.sensor_thread = threading.Thread(target=self._sensor_monitor_loop, daemon=True)
            self.sensor_thread.start()
            
            # Start communication thread
            self.communication_thread = threading.Thread(target=self._communication_loop, daemon=True)
            self.communication_thread.start()
            
            # Start heartbeat thread
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            logger.info("🔄 Hardware monitoring started")
    
    def stop_monitoring(self):
        """Stop hardware monitoring"""
        self.running = False
        
        if self.sensor_thread:
            self.sensor_thread.join(timeout=1)
        if self.communication_thread:
            self.communication_thread.join(timeout=1)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        
        logger.info("⏹️ Hardware monitoring stopped")
    
    def _sensor_monitor_loop(self):
        """Main sensor monitoring loop"""
        while self.running:
            try:
                # Read Arduino sensors
                if self.hardware_status.get('arduino') == 'connected':
                    self._read_arduino_sensors()
                
                # Read camera data
                if self.hardware_status.get('camera') == 'connected':
                    self._process_camera_frame()
                
                # Update timestamp
                self.sensor_data['timestamp'] = datetime.now().isoformat()
                
                # Trigger callbacks
                self._trigger_callbacks('sensor_update', self.sensor_data)
                
                time.sleep(self.config['sensors']['update_rate'])
                
            except Exception as e:
                logger.error(f"❌ Sensor monitoring error: {e}")
                time.sleep(1.0)
    
    def _read_arduino_sensors(self):
        """Read data from Arduino sensors"""
        try:
            # Read analog sensors
            if self.analog_pins['distance_sensor'].read() is not None:
                self.sensor_data['distance'] = self.analog_pins['distance_sensor'].read() * 100  # Convert to cm
            
            if self.analog_pins['light_sensor'].read() is not None:
                self.sensor_data['light_level'] = self.analog_pins['light_sensor'].read() * 100  # Convert to percentage
            
            if self.analog_pins['microphone'].read() is not None:
                self.sensor_data['sound_level'] = self.analog_pins['microphone'].read() * 100  # Convert to percentage
        
        except Exception as e:
            logger.error(f"❌ Arduino sensor reading error: {e}")
    
    def _process_camera_frame(self):
        """Process camera frame for gesture recognition"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                return
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                self.sensor_data['hands_detected'] = len(results.multi_hand_landmarks)
                # Process gesture recognition here
                gesture = self._recognize_gesture(results.multi_hand_landmarks[0])
                if gesture:
                    self.sensor_data['current_gesture'] = gesture
            else:
                self.sensor_data['hands_detected'] = 0
                self.sensor_data['current_gesture'] = None
        
        except Exception as e:
            logger.error(f"❌ Camera processing error: {e}")
    
    def _recognize_gesture(self, landmarks):
        """Recognize specific gestures from hand landmarks"""
        # Implement gesture recognition logic
        # This is a simplified version - extend based on your needs
        
        # Get landmark positions
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]
        
        # Simple thumbs up detection
        if thumb_tip.y < thumb_ip.y and index_tip.y > index_pip.y:
            return "thumbs_up"
        
        # Add more gesture recognition logic here
        return None
    
    def _communication_loop(self):
        """Handle communication with robot"""
        while self.running:
            try:
                if self.hardware_status.get('serial') == 'connected' and self.serial_connection:
                    # Check for incoming messages
                    if self.serial_connection.in_waiting > 0:
                        message = self.serial_connection.readline().decode().strip()
                        if message:
                            self._process_robot_message(message)
                
                time.sleep(0.01)  # High frequency for responsive communication
                
            except Exception as e:
                logger.error(f"❌ Communication error: {e}")
                time.sleep(1.0)
    
    def _process_robot_message(self, message: str):
        """Process incoming message from robot"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'status':
                self.sensor_data['robot_status'] = data.get('data', {})
            elif msg_type == 'sensor':
                self.sensor_data.update(data.get('data', {}))
            elif msg_type == 'response':
                self._trigger_callbacks('robot_response', data.get('data'))
            
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Invalid JSON from robot: {message}")
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    def _heartbeat_loop(self):
        """Send periodic heartbeat to maintain connection"""
        while self.running:
            try:
                if self.hardware_status.get('serial') == 'connected':
                    heartbeat = {
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    }
                    self.send_robot_command(heartbeat)
                
                time.sleep(5.0)  # 5-second heartbeat
                
            except Exception as e:
                logger.error(f"❌ Heartbeat error: {e}")
                time.sleep(5.0)
    
    def send_robot_command(self, command: Dict[str, Any]) -> bool:
        """Send command to robot via serial"""
        try:
            if self.hardware_status.get('serial') != 'connected':
                logger.warning("⚠️ Serial not connected - command ignored")
                return False
            
            message = json.dumps(command) + '\n'
            self.serial_connection.write(message.encode())
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send robot command: {e}")
            return False
    
    def move_robot(self, action: str, params: Dict[str, Any] = None) -> bool:
        """Send movement command to robot"""
        command = {
            'type': 'movement',
            'action': action,
            'params': params or {}
        }
        return self.send_robot_command(command)
    
    def control_servo(self, servo_name: str, angle: int) -> bool:
        """Control servo motor"""
        if self.hardware_status.get('arduino') != 'connected':
            logger.warning("⚠️ Arduino not connected - servo command ignored")
            return False
        
        try:
            if servo_name in self.servo_pins:
                self.servo_pins[servo_name].write(angle)
                return True
            else:
                logger.warning(f"⚠️ Unknown servo: {servo_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Servo control error: {e}")
            return False
    
    def set_led(self, led_name: str, state: bool) -> bool:
        """Control LED"""
        if self.hardware_status.get('arduino') != 'connected':
            logger.warning("⚠️ Arduino not connected - LED command ignored")
            return False
        
        try:
            if led_name in self.digital_pins:
                self.digital_pins[led_name].write(1 if state else 0)
                return True
            else:
                logger.warning(f"⚠️ Unknown LED: {led_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ LED control error: {e}")
            return False
    
    def speak(self, text: str) -> bool:
        """Make robot speak"""
        if self.hardware_status.get('speech') != 'connected':
            logger.warning("⚠️ Speech not available - using robot TTS if available")
            # Try to send to robot instead
            return self.send_robot_command({
                'type': 'speak',
                'text': text
            })
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"❌ Speech synthesis error: {e}")
            return False
    
    def listen(self, timeout: float = None) -> Optional[str]:
        """Listen for speech input"""
        if self.hardware_status.get('speech') != 'connected':
            logger.warning("⚠️ Speech recognition not available")
            return None
        
        try:
            timeout = timeout or self.config['speech']['recognition_timeout']
            
            with self.microphone as source:
                logger.info("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            logger.info("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"📝 Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.info("⏰ Speech recognition timeout")
            return None
        except sr.UnknownValueError:
            logger.info("❓ Could not understand speech")
            return None
        except Exception as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return None
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for hardware events"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, data: Any = None):
        """Trigger registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"❌ Callback error for {event}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive hardware status"""
        return {
            'connected': self.is_connected,
            'hardware_status': self.hardware_status,
            'sensor_data': self.sensor_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Safely shutdown hardware connections"""
        logger.info("🔌 Shutting down hardware connections...")
        
        self.stop_monitoring()
        
        # Close Arduino
        if self.arduino:
            try:
                self.arduino.exit()
            except:
                pass
        
        # Close serial
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except:
                pass
        
        # Close camera
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
        
        logger.info("✅ Hardware shutdown complete")

# Global hardware controller instance
hardware_controller = None

def get_hardware_controller(config: Dict[str, Any] = None) -> RealHardwareController:
    """Get global hardware controller instance"""
    global hardware_controller
    if hardware_controller is None:
        hardware_controller = RealHardwareController(config)
    return hardware_controller

def initialize_hardware(config: Dict[str, Any] = None) -> RealHardwareController:
    """Initialize and start hardware controller"""
    controller = get_hardware_controller(config)
    controller.start_monitoring()
    return controller