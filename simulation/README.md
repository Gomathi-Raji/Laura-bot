# 🤖 Laura-bot IoT Simulation

A comprehensive simulation environment for the Laura-bot voice assistant IoT project, allowing you to test all features without requiring physical hardware.

## 🌟 Features

### Virtual Hardware Components
- **Mock Arduino**: Simulates servo control and digital pin operations
- **Virtual Camera**: Gesture recognition without physical camera
- **Sensor Network**: 10+ environmental sensors with realistic data patterns
- **Device Management**: Connection simulation, failure testing, and restoration

### Interactive Interfaces
- **IoT Dashboard**: Web-based control panel with real-time monitoring
- **Gesture Simulator**: Visual hand gesture controls
- **Voice Assistant**: Full AI integration with simulated hardware responses
- **Activity Logging**: Comprehensive system monitoring and data export

### Realistic Simulation
- **Environmental Patterns**: Daily cycles for temperature, lighting, motion
- **Alert System**: Configurable thresholds with warning/critical notifications  
- **Data Persistence**: JSON logging with historical data retention
- **Hardware Failures**: Simulate and test error handling scenarios

## 🚀 Quick Start

### Option 1: One-Click Launch
```bash
cd Laura-bot
python simulation/launcher.py
```

### Option 2: Individual Components

#### Start IoT Dashboard
```bash
streamlit run simulation/iot_dashboard.py
```

#### Launch Gesture Simulator
```bash
python simulation/gesture_simulator.py
```

#### Test Sensor Network
```bash
python simulation/sensor_simulation.py
```

## 📊 Dashboard Features

Access the web dashboard at: http://localhost:8501

### Real-time Monitoring
- **System Overview**: Device status, sensor counts, alert summary
- **Sensor Readings**: Live data with color-coded status indicators
- **Data Visualization**: Charts, gauges, and trend analysis
- **Alert Management**: Critical and warning notifications

### Interactive Controls
- **Start/Stop Simulation**: Full system control
- **Gesture Triggers**: Manual gesture simulation
- **Device Management**: Simulate failures and restoration
- **Data Export**: JSON export of all sensor data and alerts

## 🤲 Gesture Simulation

### Available Gestures
| Gesture | Left Hand | Right Hand | Description |
|---------|-----------|------------|-------------|
| Hi | 01000 | 01000 | 👋 Greeting |
| Ambulance | 01000 | 00100 | 🚑 Medical Help |
| Fire | 01100 | 01100 | 🔥 Fire Emergency |
| Sick | 00001 | 00001 | 🤒 Health Issue |
| Water | 10000 | 10000 | 💧 Need Water |
| Up | 01000 | 00000 | ⬆️ Move Up |
| Down | 00000 | 01000 | ⬇️ Move Down |
| Danger | 00001 | 01000 | ⚠️ Warning |
| Stop | 00100 | 00100 | ✋ Stop Action |
| Wait | 00010 | 00010 | ⏸️ Wait/Pause |

### Finger Encoding
- 1 = Finger extended
- 0 = Finger closed
- Order: Thumb, Index, Middle, Ring, Pinky

## 🌡️ Sensor Network

### Sensor Types
- **Temperature** (2 sensors): Living room, bedroom
- **Humidity** (2 sensors): Living room, bathroom  
- **Air Quality**: AQI monitoring
- **Noise Level**: Decibel measurements
- **Light Level**: Lux readings
- **Motion Detection**: Movement intensity
- **Gas Level**: Kitchen monitoring
- **Pressure**: Atmospheric readings

### Realistic Patterns
- **Daily Cycles**: Temperature follows sun patterns
- **Correlated Data**: Humidity inverse to temperature
- **Activity Patterns**: Motion higher during day
- **Environmental Events**: Random spikes and variations

## 🔧 Hardware Simulation

### Mock Arduino
```python
from simulation.iot_hardware_sim import get_mock_arduino

# Replace original Arduino
board = get_mock_arduino('COM7')
board.digital[9].write(90)  # Servo control
```

### Virtual Camera
```python
from simulation.iot_hardware_sim import get_mock_camera

# Replace OpenCV camera
cap = get_mock_camera()
ret, frame = cap.read()  # Returns mock data
```

## 📝 Integration with Existing Code

### Voice Assistant Integration
The simulation works with your existing `main.py` and `app_ui.py`:

```python
# In your existing voice/speaker.py
try:
    from pyfirmata import Arduino
    board = Arduino('COM7')
except ImportError:
    # Simulation mode
    from simulation.iot_hardware_sim import get_mock_arduino
    board = get_mock_arduino('COM7')
```

### Gesture Recognition Replacement
```python
# In your existing gesture/gesture.py
try:
    import cv2
    cap = cv2.VideoCapture("http://10.170.105.110:81/stream")
except:
    # Simulation mode
    from simulation.iot_hardware_sim import get_mock_camera
    cap = get_mock_camera()
```

## 🚨 Alert System

### Threshold Configuration
```python
thresholds = {
    "temperature": {"warning": (30, 35), "critical": (35, 45)},
    "humidity": {"warning": (70, 80), "critical": (80, 95)},
    "air_quality": {"warning": (150, 200), "critical": (200, 300)}
}
```

### Alert Types
- **Warning**: Yellow indicators, logged notifications
- **Critical**: Red alerts, immediate attention required
- **Historical**: Last 50 alerts retained with timestamps

## 📊 Data Export

Export formats:
- **JSON**: Complete sensor data with metadata
- **CSV**: Tabular data for analysis
- **Log Files**: Detailed activity logs

## 🛠️ Advanced Configuration

### Custom Sensor Values
```python
from simulation.sensor_simulation import sensor_simulator

# Simulate specific conditions
sensor_simulator.sensors["temp_001"]["current_value"] = 40.0
sensor_simulator.simulate_sensor_failure("hum_001")
```

### Gesture Callbacks
```python
from simulation.iot_hardware_sim import gesture_simulator

def my_gesture_handler(gesture_name, finger_pattern):
    print(f"Custom handler: {gesture_name}")

gesture_simulator.add_gesture_callback(my_gesture_handler)
```

## 🎯 Use Cases

### Development Testing
- Test voice commands without hardware
- Validate gesture recognition logic
- Debug sensor threshold algorithms
- Prototype new IoT features

### Demonstration
- Show IoT capabilities without setup
- Present to stakeholders/investors
- Educational demonstrations
- Remote presentations

### Continuous Integration
- Automated testing in CI/CD pipelines
- Hardware-independent unit tests
- Integration testing scenarios
- Performance benchmarking

## 🔍 Troubleshooting

### Common Issues

**Dashboard won't start**
```bash
pip install streamlit plotly pandas
streamlit run simulation/iot_dashboard.py
```

**Gesture simulator error**
```bash
pip install opencv-python mediapipe
python simulation/gesture_simulator.py
```

**Import errors**
```bash
# Ensure Python path includes project root
export PYTHONPATH="${PYTHONPATH}:/path/to/Laura-bot"
```

### Performance Optimization
- Reduce sensor update frequency for slower systems
- Limit historical data retention
- Disable unused simulation components

## 📈 Monitoring & Analytics

### Real-time Metrics
- Device uptime and connection status
- Sensor reading frequencies and patterns
- Alert generation rates and severity
- System resource utilization

### Historical Analysis
- Sensor data trends over time
- Alert pattern analysis
- Device reliability statistics
- Performance optimization insights

## 🔄 Future Enhancements

### Planned Features
- **3D Visualization**: Physical device layout simulation
- **Mobile Dashboard**: Responsive web interface
- **Cloud Integration**: Remote monitoring capabilities
- **ML Analytics**: Predictive maintenance and anomaly detection
- **VR/AR Interface**: Immersive IoT environment

### Extension Points
- Custom sensor types and patterns
- External data source integration
- Third-party dashboard plugins
- Advanced alert routing systems

## 🤝 Contributing

To add new simulation components:

1. **New Sensor Type**:
   ```python
   # Add to sensor_simulation.py
   sensor_configs.append({
       "id": "custom_001", 
       "type": "custom_sensor",
       "unit": "units",
       "base": 50.0,
       "location": "custom_location"
   })
   ```

2. **New Gesture**:
   ```python
   # Add to gesture_simulator.py
   gesture_map["Custom Gesture"] = ("11000", "00011")
   ```

3. **Dashboard Widget**:
   ```python
   # Add to iot_dashboard.py
   def render_custom_widget(self):
       st.subheader("Custom Widget")
       # Your custom visualization
   ```

## 📞 Support

For issues and questions:
- Check the activity log in the launcher
- Review console output for error details
- Ensure all dependencies are installed
- Verify Python path configuration

---

**Made with ❤️ for the Laura-bot IoT ecosystem**