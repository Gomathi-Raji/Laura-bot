# 🤖 Laura-bot Hardware Integration Guide

This guide helps you connect and configure real hardware components with your Laura-bot system.

## 🔧 Supported Hardware Components

### Required Components
- **Arduino Board** (Uno, Nano, ESP32, etc.)
- **USB Cable** for Arduino connection
- **Computer with USB ports**

### Optional Components
- **Servo Motors** (for head movement, arms)
- **LEDs** (status indicators, eyes)
- **Ultrasonic Sensor** (distance measurement)
- **Microphone** (speech recognition)
- **Speaker** (text-to-speech)
- **Camera/Webcam** (vision, gesture recognition)
- **Additional Robot Hardware** (wheels, motors, sensors)

## 🚀 Quick Setup

### 1. Install Hardware Dependencies
```bash
# Run the automated setup
setup_hardware.bat

# Or install manually
pip install -r hardware_requirements.txt
```

### 2. Hardware Configuration
```bash
# Run the configuration tool
python hardware/setup_hardware.py
```

### 3. Connect Your Hardware
1. **Arduino Connection:**
   - Connect Arduino via USB
   - Note the COM port (e.g., COM7)
   - Upload StandardFirmata to Arduino (optional for advanced control)

2. **Servo Connections:**
   ```
   Head Pan Servo  -> Pin 9
   Head Tilt Servo -> Pin 10
   Left Arm Servo  -> Pin 6
   Right Arm Servo -> Pin 5
   ```

3. **LED Connections:**
   ```
   Status LED -> Pin 13 (built-in)
   Eye LEDs   -> Pin 12
   ```

4. **Sensor Connections:**
   ```
   Ultrasonic Sensor -> Pin A0
   Light Sensor      -> Pin A1
   Microphone        -> Pin A2
   ```

### 4. Start Laura-bot
```bash
# Start the server with hardware integration
python laura_bot_server.py
```

## 🎛️ Hardware Control Interface

Once connected, access the hardware control panel at:
**http://localhost:5555/hardware**

### Available Controls:

#### 🤖 Servo Control
- **Head Pan/Tilt:** Control robot head movement
- **Arm Control:** Move left and right arms
- **Preset Positions:** Ready, Greeting, Thinking, Celebration

#### 💡 LED Control
- **Status LED:** System status indicator
- **Eye LEDs:** Expressive lighting
- **LED Patterns:** Blink, pulse, rainbow effects

#### 🚗 Movement Control
- **Directional Pad:** Forward, backward, left, right
- **Speed Control:** Adjustable movement speed
- **Emergency Stop:** Immediate halt

#### 🎤 Speech Control
- **Text-to-Speech:** Make Laura-bot speak
- **Speech Recognition:** Voice command input
- **Voice Settings:** Rate and volume control

#### 📊 Sensor Monitoring
- **Distance Sensor:** Obstacle detection
- **Light Sensor:** Ambient light measurement
- **Sound Level:** Audio input monitoring
- **Gesture Recognition:** Hand gesture detection

## 🔌 Hardware Configuration

### Arduino Setup

1. **Install Arduino IDE**
2. **Install StandardFirmata (optional):**
   ```
   File -> Examples -> Firmata -> StandardFirmata
   Upload to Arduino
   ```

3. **Basic Circuit Example:**
   ```
   Arduino Uno Connections:
   ========================
   Pin 9  -> Head Pan Servo (PWM)
   Pin 10 -> Head Tilt Servo (PWM)
   Pin 6  -> Left Arm Servo (PWM)
   Pin 5  -> Right Arm Servo (PWM)
   Pin 13 -> Status LED (built-in)
   Pin 12 -> Eye LEDs
   Pin A0 -> Ultrasonic Sensor (Trig/Echo)
   Pin A1 -> Light Sensor (LDR)
   Pin A2 -> Microphone (analog)
   ```

### Serial Communication

For advanced robot platforms:
1. **Connect via Serial/USB**
2. **Configure baud rate:** 115200
3. **Protocol:** JSON messages
4. **Example message format:**
   ```json
   {
     "type": "movement",
     "action": "forward",
     "params": {"speed": 50}
   }
   ```

### Camera Setup

1. **USB Webcam:** Plug and play
2. **Raspberry Pi Camera:** Enable camera interface
3. **IP Camera:** Configure network settings

## 🛠️ Troubleshooting

### Common Issues

#### Arduino Not Detected
- **Check USB connection**
- **Install Arduino drivers**
- **Try different USB port**
- **Check COM port in Device Manager**

#### Servo Not Moving
- **Check power supply (servos need 5V)**
- **Verify pin connections**
- **Test with simple Arduino sketch**

#### Speech Not Working
- **Check microphone permissions**
- **Install audio drivers**
- **Test microphone in system settings**

#### Camera Not Found
- **Check camera permissions**
- **Close other camera applications**
- **Try different camera index (0, 1, 2...)**

### Error Messages

#### "Hardware controller not available"
- Install required dependencies: `pip install -r hardware_requirements.txt`
- Check hardware connections
- Run hardware setup: `python hardware/setup_hardware.py`

#### "Arduino connection failed"
- Check COM port configuration
- Verify Arduino is connected and powered
- Install Arduino drivers

#### "Serial communication failed"
- Check baud rate settings
- Verify serial port permissions
- Try different USB cable

## 🔍 Testing Hardware

### Manual Testing
```bash
# Run comprehensive hardware test
python hardware/setup_hardware.py

# Test individual components
python -c "from hardware.real_hardware_controller import initialize_hardware; controller = initialize_hardware()"
```

### Hardware Status Check
- Access dashboard: http://localhost:5555/
- Check hardware status indicators
- Monitor sensor readings in real-time

## 📡 Advanced Configuration

### Custom Hardware Config
Create `hardware/hardware_config.json`:
```json
{
  "arduino": {
    "port": "COM7",
    "baudrate": 9600
  },
  "serial": {
    "port": "COM3",
    "baudrate": 115200
  },
  "camera": {
    "device_id": 0,
    "width": 640,
    "height": 480
  }
}
```

### Multiple Arduino Support
```python
# Configure multiple Arduino boards
config = {
  "arduino_main": {"port": "COM7"},
  "arduino_sensors": {"port": "COM8"}
}
```

### Network Robot Integration
```python
# For WiFi-enabled robots
config = {
  "robot": {
    "ip_address": "192.168.1.100",
    "port": 8080,
    "protocol": "tcp"
  }
}
```

## 🎯 Example Implementations

### Basic Servo Robot
```python
# Simple servo control example
controller = get_hardware_controller()
controller.control_servo("head_pan", 90)
controller.control_servo("head_tilt", 45)
```

### Speech-Enabled Robot
```python
# Text-to-speech example
controller.speak("Hello, I am Laura-bot!")

# Speech recognition example
text = controller.listen(timeout=5)
print(f"You said: {text}")
```

### Gesture-Controlled Robot
```python
# Gesture recognition callback
def on_gesture(gesture):
    if gesture == "thumbs_up":
        controller.control_servo("head_tilt", 60)  # Nod
        controller.speak("Thank you!")

controller.register_callback('gesture_detected', on_gesture)
```

## 📚 Additional Resources

- **Arduino Documentation:** https://www.arduino.cc/en/Guide
- **Servo Control Guide:** https://www.arduino.cc/en/tutorial/sweep
- **OpenCV Camera Tutorial:** https://opencv-python-tutroals.readthedocs.io/
- **Speech Recognition Guide:** https://pypi.org/project/SpeechRecognition/

## 🆘 Support

If you encounter issues:

1. **Check the hardware setup log**
2. **Run diagnostics:** `python hardware/setup_hardware.py`
3. **Review error messages** in the server console
4. **Test individual components** separately
5. **Check hardware connections** and power supply

## 🔐 Safety Notes

- **Power Supply:** Ensure adequate power for servos and motors
- **Voltage Levels:** Match voltage requirements (3.3V vs 5V)
- **Current Limits:** Don't exceed Arduino pin current limits
- **Emergency Stop:** Always have a way to quickly stop movement
- **Supervision:** Never leave autonomous robots unattended

---

Happy robot building! 🤖✨