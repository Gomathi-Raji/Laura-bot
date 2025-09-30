"""
Arduino Educational Controller
Integrates Arduino hardware with Laura-bot learning system
Provides gesture recognition, servo control, and educational interactions
"""

import time
import threading
import random
from typing import Dict, Any, Optional
import json

try:
    from pyfirmata import Arduino, util
    ARDUINO_AVAILABLE = True
except ImportError:
    print("⚠️ PyFirmata not available. Running in simulation mode.")
    ARDUINO_AVAILABLE = False

try:
    import cv2
    import mediapipe as mp
    CAMERA_AVAILABLE = True
except ImportError:
    print("⚠️ Camera/MediaPipe not available. Gesture recognition disabled.")
    CAMERA_AVAILABLE = False

class ArduinoEducationalController:
    def __init__(self, port='COM7'):
        self.port = port
        self.board = None
        self.servo_pins = {
            'servo1': 9,
            'servo2': 10,
            'led_pin': 13
        }
        self.is_connected = False
        self.gesture_active = False
        self.learning_mode = False
        self.current_gesture = None
        
        # Educational gesture mappings
        self.educational_gestures = {
            'thumbs_up': 'correct_answer',
            'thumbs_down': 'incorrect_answer',
            'open_palm': 'ready_to_learn',
            'fist': 'thinking',
            'peace': 'next_question',
            'pointing': 'select_option'
        }
        
        # Servo positions for different educational states
        self.servo_positions = {
            'ready': {'servo1': 90, 'servo2': 90},
            'celebration': {'servo1': 180, 'servo2': 0},
            'thinking': {'servo1': 45, 'servo2': 135},
            'correct': {'servo1': 150, 'servo2': 30},
            'incorrect': {'servo1': 30, 'servo2': 150},
            'listening': {'servo1': 120, 'servo2': 60}
        }
        
        self.initialize_hardware()
    
    def initialize_hardware(self):
        """Initialize Arduino connection and setup pins"""
        if not ARDUINO_AVAILABLE:
            print("🤖 Running in simulation mode - Arduino features simulated")
            self.is_connected = False
            return
        
        try:
            print(f"🔌 Connecting to Arduino on {self.port}...")
            self.board = Arduino(self.port)
            
            # Setup servo pins
            self.servo1 = self.board.get_pin(f'd:{self.servo_pins["servo1"]}:s')
            self.servo2 = self.board.get_pin(f'd:{self.servo_pins["servo2"]}:s')
            self.led = self.board.get_pin(f'd:{self.servo_pins["led_pin"]}:o')
            
            # Start the iterator to read data from Arduino
            self.iterator = util.Iterator(self.board)
            self.iterator.start()
            
            self.is_connected = True
            print("✅ Arduino connected successfully!")
            
            # Initial position
            self.move_to_position('ready')
            
        except Exception as e:
            print(f"⚠️ Arduino connection failed: {e}")
            print("🤖 Running in simulation mode")
            self.is_connected = False
    
    def move_to_position(self, position_name: str, duration: float = 1.0):
        """Move servos to predefined educational position"""
        if position_name not in self.servo_positions:
            print(f"⚠️ Unknown position: {position_name}")
            return
        
        if self.is_connected:
            try:
                position = self.servo_positions[position_name]
                self.servo1.write(position['servo1'])
                self.servo2.write(position['servo2'])
                
                # LED indication
                if position_name == 'correct':
                    self.blink_led(3, 0.2)  # Fast blinks for correct
                elif position_name == 'incorrect':
                    self.blink_led(1, 1.0)  # Slow blink for incorrect
                
                print(f"🤖 Moved to position: {position_name}")
                
            except Exception as e:
                print(f"⚠️ Servo movement error: {e}")
        else:
            # Simulation mode
            print(f"🤖 [SIMULATION] Moved to position: {position_name}")
        
        time.sleep(duration)
    
    def blink_led(self, count: int, duration: float):
        """Blink LED for feedback"""
        if not self.is_connected:
            print(f"🤖 [SIMULATION] LED blink {count} times")
            return
        
        def blink_thread():
            try:
                for _ in range(count):
                    self.led.write(1)
                    time.sleep(duration / 2)
                    self.led.write(0)
                    time.sleep(duration / 2)
            except Exception as e:
                print(f"⚠️ LED error: {e}")
        
        threading.Thread(target=blink_thread, daemon=True).start()
    
    def celebration_sequence(self):
        """Perform celebration sequence for correct answers or achievements"""
        print("🎉 Celebration sequence!")
        
        if self.is_connected:
            try:
                # Dance sequence
                positions = ['celebration', 'ready', 'celebration', 'ready']
                for pos in positions:
                    self.move_to_position(pos, 0.5)
                
                # Victory LED pattern
                self.blink_led(5, 0.3)
                
            except Exception as e:
                print(f"⚠️ Celebration error: {e}")
        else:
            print("🤖 [SIMULATION] 🎉 Celebration dance performed!")
    
    def thinking_animation(self, duration: float = 3.0):
        """Animate thinking/processing"""
        print("🤔 Thinking animation...")
        
        if self.is_connected:
            try:
                # Subtle back-and-forth movement
                start_time = time.time()
                while time.time() - start_time < duration:
                    self.move_to_position('thinking', 0.5)
                    self.move_to_position('ready', 0.5)
                
            except Exception as e:
                print(f"⚠️ Thinking animation error: {e}")
        else:
            print(f"🤖 [SIMULATION] 🤔 Thinking for {duration} seconds...")
            time.sleep(duration)
    
    def quiz_feedback(self, correct: bool, explanation: str = ""):
        """Provide hardware feedback for quiz answers"""
        if correct:
            print("✅ Correct answer feedback!")
            self.move_to_position('correct', 1.0)
            self.celebration_sequence()
        else:
            print("❌ Incorrect answer feedback")
            self.move_to_position('incorrect', 1.0)
            self.blink_led(2, 0.5)
        
        # Return to ready position
        time.sleep(1)
        self.move_to_position('ready')
    
    def start_gesture_recognition(self):
        """Start gesture recognition for educational interactions"""
        if not CAMERA_AVAILABLE:
            print("⚠️ Camera not available for gesture recognition")
            return False
        
        self.gesture_active = True
        self.gesture_thread = threading.Thread(target=self._gesture_recognition_loop, daemon=True)
        self.gesture_thread.start()
        print("👋 Gesture recognition started")
        return True
    
    def stop_gesture_recognition(self):
        """Stop gesture recognition"""
        self.gesture_active = False
        print("👋 Gesture recognition stopped")
    
    def _gesture_recognition_loop(self):
        """Main gesture recognition loop"""
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        mp_draw = mp.solutions.drawing_utils
        
        cap = cv2.VideoCapture(0)
        
        try:
            while self.gesture_active:
                success, img = cap.read()
                if not success:
                    continue
                
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks
                        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        # Detect gesture
                        gesture = self._classify_gesture(hand_landmarks)
                        if gesture and gesture != self.current_gesture:
                            self.current_gesture = gesture
                            self._handle_educational_gesture(gesture)
                
                # Display the image
                cv2.imshow("Laura-bot Gesture Control", img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except Exception as e:
            print(f"⚠️ Gesture recognition error: {e}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def _classify_gesture(self, landmarks) -> Optional[str]:
        """Classify hand gesture from landmarks"""
        # Simple gesture classification based on landmark positions
        # This is a simplified version - you can enhance with more sophisticated ML models
        
        # Get landmark positions
        thumb_tip = landmarks.landmark[4]
        thumb_ip = landmarks.landmark[3]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        # Thumbs up detection
        if thumb_tip.y < thumb_ip.y and index_tip.y > landmarks.landmark[6].y:
            return 'thumbs_up'
        
        # Open palm detection
        if (index_tip.y < landmarks.landmark[6].y and 
            middle_tip.y < landmarks.landmark[10].y and
            ring_tip.y < landmarks.landmark[14].y and
            pinky_tip.y < landmarks.landmark[18].y):
            return 'open_palm'
        
        # Fist detection
        if (index_tip.y > landmarks.landmark[6].y and 
            middle_tip.y > landmarks.landmark[10].y and
            ring_tip.y > landmarks.landmark[14].y and
            pinky_tip.y > landmarks.landmark[18].y):
            return 'fist'
        
        # Peace sign (V)
        if (index_tip.y < landmarks.landmark[6].y and 
            middle_tip.y < landmarks.landmark[10].y and
            ring_tip.y > landmarks.landmark[14].y and
            pinky_tip.y > landmarks.landmark[18].y):
            return 'peace'
        
        return None
    
    def _handle_educational_gesture(self, gesture: str):
        """Handle detected educational gesture"""
        if gesture in self.educational_gestures:
            action = self.educational_gestures[gesture]
            print(f"👋 Gesture detected: {gesture} -> {action}")
            
            # Provide immediate hardware feedback
            if action == 'correct_answer':
                self.move_to_position('correct', 0.5)
            elif action == 'incorrect_answer':
                self.move_to_position('incorrect', 0.5)
            elif action == 'ready_to_learn':
                self.move_to_position('ready', 0.5)
            elif action == 'thinking':
                self.move_to_position('thinking', 0.5)
            elif action == 'next_question':
                self.blink_led(2, 0.3)
            
            return action
        
        return None
    
    def learning_mode_animation(self, mode: str):
        """Provide visual feedback for different learning modes"""
        animations = {
            'quiz_start': lambda: self.move_to_position('ready'),
            'quiz_end': lambda: self.celebration_sequence(),
            'explanation_mode': lambda: self.move_to_position('listening'),
            'practice_mode': lambda: self.thinking_animation(2.0),
            'session_start': lambda: self._welcome_sequence(),
            'session_end': lambda: self._goodbye_sequence()
        }
        
        if mode in animations:
            print(f"🎭 Learning animation: {mode}")
            animations[mode]()
    
    def _welcome_sequence(self):
        """Welcome animation for new learning session"""
        print("👋 Welcome sequence!")
        self.move_to_position('celebration', 0.5)
        self.move_to_position('ready', 0.5)
        self.blink_led(3, 0.2)
    
    def _goodbye_sequence(self):
        """Goodbye animation for ending session"""
        print("👋 Goodbye sequence!")
        positions = ['ready', 'celebration', 'ready']
        for pos in positions:
            self.move_to_position(pos, 0.8)
        self.blink_led(2, 0.5)
    
    def test_all_functions(self):
        """Test all hardware functions"""
        print("🧪 Testing all Arduino educational functions...")
        
        tests = [
            ('Ready Position', lambda: self.move_to_position('ready')),
            ('Thinking Animation', lambda: self.thinking_animation(2.0)),
            ('Correct Answer', lambda: self.quiz_feedback(True)),
            ('Incorrect Answer', lambda: self.quiz_feedback(False)),
            ('Celebration', lambda: self.celebration_sequence()),
            ('Welcome Sequence', lambda: self._welcome_sequence()),
            ('LED Test', lambda: self.blink_led(5, 0.3))
        ]
        
        for test_name, test_func in tests:
            print(f"🔧 Testing: {test_name}")
            test_func()
            time.sleep(1)
        
        print("✅ All tests completed!")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current controller status"""
        return {
            'connected': self.is_connected,
            'port': self.port,
            'gesture_active': self.gesture_active,
            'learning_mode': self.learning_mode,
            'current_gesture': self.current_gesture,
            'hardware_available': ARDUINO_AVAILABLE,
            'camera_available': CAMERA_AVAILABLE
        }
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up Arduino controller...")
        
        if self.gesture_active:
            self.stop_gesture_recognition()
        
        if self.is_connected and self.board:
            try:
                # Return to neutral position
                self.move_to_position('ready')
                self.led.write(0)  # Turn off LED
                self.board.exit()
                print("✅ Arduino disconnected safely")
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")
        
        self.is_connected = False

# Usage example and testing
if __name__ == "__main__":
    controller = ArduinoEducationalController()
    
    try:
        print("🤖 Laura-bot Arduino Educational Controller")
        print("Status:", controller.get_status())
        
        # Run tests
        controller.test_all_functions()
        
        # Optionally start gesture recognition
        choice = input("\nStart gesture recognition? (y/n): ").lower()
        if choice == 'y':
            controller.start_gesture_recognition()
            input("Press Enter to stop gesture recognition...")
            controller.stop_gesture_recognition()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping controller...")
    
    finally:
        controller.cleanup()
        print("👋 Goodbye!")