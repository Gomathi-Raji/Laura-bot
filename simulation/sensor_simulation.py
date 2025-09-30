"""
IoT Sensor Data Simulation
=========================
Advanced sensor simulation with realistic data patterns, alerts, and IoT device monitoring.
"""

import time
import random
import threading
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import ttk


@dataclass
class SensorReading:
    """Data class for sensor readings"""
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    status: str = "normal"  # normal, warning, critical
    location: str = "living_room"


class AdvancedSensorSimulator:
    """Advanced IoT sensor simulation with realistic patterns"""
    
    def __init__(self):
        self.sensors = {}
        self.sensor_history = {}
        self.alerts = []
        self.is_running = False
        self.simulation_thread = None
        
        # Initialize sensors
        self.initialize_sensors()
        
        # Alert thresholds
        self.thresholds = {
            "temperature": {"warning": (30, 35), "critical": (35, 45)},
            "humidity": {"warning": (70, 80), "critical": (80, 95)},
            "air_quality": {"warning": (150, 200), "critical": (200, 300)},
            "noise_level": {"warning": (70, 85), "critical": (85, 100)},
            "light_level": {"warning": (100, 200), "critical": (50, 100)},
            "motion_intensity": {"warning": (7, 9), "critical": (9, 10)}
        }
    
    def initialize_sensors(self):
        """Initialize all sensors with base values"""
        sensor_configs = [
            {"id": "temp_001", "type": "temperature", "unit": "°C", "base": 24.0, "location": "living_room"},
            {"id": "temp_002", "type": "temperature", "unit": "°C", "base": 22.0, "location": "bedroom"},
            {"id": "hum_001", "type": "humidity", "unit": "%", "base": 55.0, "location": "living_room"},
            {"id": "hum_002", "type": "humidity", "unit": "%", "base": 60.0, "location": "bathroom"},
            {"id": "air_001", "type": "air_quality", "unit": "AQI", "base": 95.0, "location": "living_room"},
            {"id": "noise_001", "type": "noise_level", "unit": "dB", "base": 40.0, "location": "living_room"},
            {"id": "light_001", "type": "light_level", "unit": "lux", "base": 400.0, "location": "living_room"},
            {"id": "motion_001", "type": "motion_intensity", "unit": "scale", "base": 2.0, "location": "entrance"},
            {"id": "gas_001", "type": "gas_level", "unit": "ppm", "base": 10.0, "location": "kitchen"},
            {"id": "pressure_001", "type": "pressure", "unit": "hPa", "base": 1013.25, "location": "outdoor"}
        ]
        
        for config in sensor_configs:
            self.sensors[config["id"]] = {
                "type": config["type"],
                "unit": config["unit"],
                "base_value": config["base"],
                "current_value": config["base"],
                "location": config["location"],
                "trend": 0.0,
                "variance": self.get_variance_for_type(config["type"]),
                "last_reading": datetime.now()
            }
            self.sensor_history[config["id"]] = []
    
    def get_variance_for_type(self, sensor_type: str) -> float:
        """Get realistic variance for different sensor types"""
        variances = {
            "temperature": 2.0,
            "humidity": 5.0,
            "air_quality": 15.0,
            "noise_level": 8.0,
            "light_level": 50.0,
            "motion_intensity": 1.0,
            "gas_level": 3.0,
            "pressure": 5.0
        }
        return variances.get(sensor_type, 1.0)
    
    def start_simulation(self):
        """Start the sensor simulation"""
        if not self.is_running:
            self.is_running = True
            self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.simulation_thread.start()
            print("🚀 Advanced sensor simulation started")
    
    def stop_simulation(self):
        """Stop the sensor simulation"""
        self.is_running = False
        print("⏹️ Sensor simulation stopped")
    
    def _simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            current_time = datetime.now()
            
            for sensor_id, sensor in self.sensors.items():
                # Update sensor reading
                new_reading = self._generate_realistic_reading(sensor_id, sensor, current_time)
                sensor["current_value"] = new_reading.value
                sensor["last_reading"] = current_time
                
                # Store in history (keep last 100 readings)
                self.sensor_history[sensor_id].append(new_reading)
                if len(self.sensor_history[sensor_id]) > 100:
                    self.sensor_history[sensor_id].pop(0)
                
                # Check for alerts
                self._check_alerts(new_reading)
            
            time.sleep(2)  # Update every 2 seconds
    
    def _generate_realistic_reading(self, sensor_id: str, sensor: Dict, timestamp: datetime) -> SensorReading:
        """Generate realistic sensor reading with patterns"""
        sensor_type = sensor["type"]
        base_value = sensor["base_value"]
        variance = sensor["variance"]
        location = sensor["location"]
        
        # Time-based patterns
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Daily patterns for different sensors
        if sensor_type == "temperature":
            # Temperature follows daily cycle
            daily_cycle = 3 * math.sin((hour - 6) * math.pi / 12)
            noise = random.uniform(-variance/2, variance/2)
            value = base_value + daily_cycle + noise
            
        elif sensor_type == "humidity":
            # Inverse correlation with temperature
            daily_cycle = -2 * math.sin((hour - 6) * math.pi / 12)
            noise = random.uniform(-variance/2, variance/2)
            value = base_value + daily_cycle + noise
            
        elif sensor_type == "light_level":
            # Light follows sun pattern
            if 6 <= hour <= 18:
                sun_cycle = 300 * math.sin((hour - 6) * math.pi / 12)
            else:
                sun_cycle = 0
            noise = random.uniform(-variance/2, variance/2)
            value = max(0, base_value + sun_cycle + noise)
            
        elif sensor_type == "motion_intensity":
            # More motion during day, random spikes
            if 7 <= hour <= 22:
                base_motion = 4.0
            else:
                base_motion = 1.0
            spike = 5.0 if random.random() < 0.1 else 0
            noise = random.uniform(-variance/2, variance/2)
            value = max(0, base_motion + spike + noise)
            
        elif sensor_type == "air_quality":
            # Worse during rush hours
            if hour in [8, 9, 17, 18, 19]:
                traffic_effect = 30
            else:
                traffic_effect = 0
            noise = random.uniform(-variance/2, variance/2)
            value = max(0, base_value + traffic_effect + noise)
            
        else:
            # Default random walk
            trend_change = random.uniform(-0.1, 0.1)
            sensor["trend"] = max(-1, min(1, sensor["trend"] + trend_change))
            noise = random.uniform(-variance/2, variance/2)
            value = base_value + sensor["trend"] * variance + noise
        
        # Determine status based on thresholds
        status = self._get_status_for_value(sensor_type, value)
        
        return SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            value=round(value, 2),
            unit=sensor["unit"],
            timestamp=timestamp.isoformat(),
            status=status,
            location=location
        )
    
    def _get_status_for_value(self, sensor_type: str, value: float) -> str:
        """Determine status based on sensor value and thresholds"""
        if sensor_type not in self.thresholds:
            return "normal"
        
        thresholds = self.thresholds[sensor_type]
        
        # Check critical thresholds
        crit_min, crit_max = thresholds["critical"]
        if value >= crit_max or value <= crit_min:
            return "critical"
        
        # Check warning thresholds
        warn_min, warn_max = thresholds["warning"]
        if value >= warn_max or value <= warn_min:
            return "warning"
        
        return "normal"
    
    def _check_alerts(self, reading: SensorReading):
        """Check for alerts and log them"""
        if reading.status in ["warning", "critical"]:
            alert = {
                "timestamp": reading.timestamp,
                "sensor_id": reading.sensor_id,
                "sensor_type": reading.sensor_type,
                "location": reading.location,
                "value": reading.value,
                "unit": reading.unit,
                "status": reading.status,
                "message": self._generate_alert_message(reading)
            }
            
            self.alerts.append(alert)
            
            # Keep only last 50 alerts
            if len(self.alerts) > 50:
                self.alerts.pop(0)
            
            print(f"🚨 {reading.status.upper()} Alert: {alert['message']}")
    
    def _generate_alert_message(self, reading: SensorReading) -> str:
        """Generate human-readable alert message"""
        messages = {
            "temperature": f"Temperature {reading.value}{reading.unit} in {reading.location}",
            "humidity": f"Humidity {reading.value}{reading.unit} in {reading.location}",
            "air_quality": f"Poor air quality (AQI: {reading.value}) in {reading.location}",
            "noise_level": f"High noise level {reading.value}{reading.unit} in {reading.location}",
            "light_level": f"Unusual light level {reading.value}{reading.unit} in {reading.location}",
            "motion_intensity": f"High motion detected in {reading.location}",
            "gas_level": f"Elevated gas level {reading.value}{reading.unit} in {reading.location}",
            "pressure": f"Pressure reading {reading.value}{reading.unit}"
        }
        
        return messages.get(reading.sensor_type, f"{reading.sensor_type}: {reading.value}{reading.unit}")
    
    def get_current_readings(self) -> List[SensorReading]:
        """Get current readings from all sensors"""
        readings = []
        for sensor_id, sensor in self.sensors.items():
            if self.sensor_history[sensor_id]:
                readings.append(self.sensor_history[sensor_id][-1])
        return readings
    
    def get_sensor_history(self, sensor_id: str, limit: int = 20) -> List[SensorReading]:
        """Get historical readings for a sensor"""
        if sensor_id in self.sensor_history:
            return self.sensor_history[sensor_id][-limit:]
        return []
    
    def get_alerts(self, status_filter: str = None, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        alerts = self.alerts[-limit:]
        if status_filter:
            alerts = [a for a in alerts if a["status"] == status_filter]
        return alerts
    
    def simulate_sensor_failure(self, sensor_id: str):
        """Simulate sensor failure"""
        if sensor_id in self.sensors:
            # Set extreme values to simulate failure
            self.sensors[sensor_id]["current_value"] = -999
            print(f"⚠️ Simulated failure for sensor {sensor_id}")
    
    def restore_sensor(self, sensor_id: str):
        """Restore failed sensor"""
        if sensor_id in self.sensors:
            self.sensors[sensor_id]["current_value"] = self.sensors[sensor_id]["base_value"]
            print(f"✅ Restored sensor {sensor_id}")
    
    def get_statistics(self) -> Dict:
        """Get sensor statistics"""
        stats = {
            "total_sensors": len(self.sensors),
            "active_sensors": sum(1 for s in self.sensors.values() if s["current_value"] != -999),
            "total_readings": sum(len(history) for history in self.sensor_history.values()),
            "total_alerts": len(self.alerts),
            "critical_alerts": len([a for a in self.alerts if a["status"] == "critical"]),
            "warning_alerts": len([a for a in self.alerts if a["status"] == "warning"]),
            "uptime": "Running" if self.is_running else "Stopped"
        }
        return stats


class IoTDataLogger:
    """Data logging system for IoT sensor data"""
    
    def __init__(self, sensor_simulator: AdvancedSensorSimulator):
        self.sensor_simulator = sensor_simulator
        self.log_file = "simulation/iot_sensor_log.json"
        self.logging_enabled = False
        self.log_thread = None
    
    def start_logging(self):
        """Start data logging"""
        if not self.logging_enabled:
            self.logging_enabled = True
            self.log_thread = threading.Thread(target=self._logging_loop, daemon=True)
            self.log_thread.start()
            print("📊 IoT data logging started")
    
    def stop_logging(self):
        """Stop data logging"""
        self.logging_enabled = False
        print("📊 IoT data logging stopped")
    
    def _logging_loop(self):
        """Main logging loop"""
        while self.logging_enabled:
            try:
                # Get current readings
                readings = self.sensor_simulator.get_current_readings()
                
                # Prepare log entry
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "readings": [asdict(reading) for reading in readings],
                    "statistics": self.sensor_simulator.get_statistics()
                }
                
                # Append to log file
                self._append_to_log(log_entry)
                
            except Exception as e:
                print(f"❌ Logging error: {e}")
            
            time.sleep(30)  # Log every 30 seconds
    
    def _append_to_log(self, log_entry: Dict):
        """Append entry to log file"""
        try:
            # Read existing log
            try:
                with open(self.log_file, 'r') as f:
                    log_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                log_data = {"log_entries": []}
            
            # Add new entry
            log_data["log_entries"].append(log_entry)
            
            # Keep only last 1000 entries
            if len(log_data["log_entries"]) > 1000:
                log_data["log_entries"] = log_data["log_entries"][-1000:]
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error writing to log file: {e}")


# Global sensor simulator instance
sensor_simulator = AdvancedSensorSimulator()
data_logger = IoTDataLogger(sensor_simulator)


if __name__ == "__main__":
    print("🌡️ Starting Advanced IoT Sensor Simulation...")
    
    # Start simulation
    sensor_simulator.start_simulation()
    data_logger.start_logging()
    
    try:
        # Run for demonstration
        time.sleep(10)
        
        # Show some readings
        print("\n📊 Current Sensor Readings:")
        readings = sensor_simulator.get_current_readings()
        for reading in readings:
            status_emoji = {"normal": "✅", "warning": "⚠️", "critical": "🚨"}
            print(f"  {status_emoji.get(reading.status, '❓')} {reading.sensor_type} ({reading.location}): {reading.value}{reading.unit}")
        
        # Show statistics
        print(f"\n📈 Statistics: {sensor_simulator.get_statistics()}")
        
        # Show recent alerts
        alerts = sensor_simulator.get_alerts()
        if alerts:
            print(f"\n🚨 Recent Alerts:")
            for alert in alerts[-3:]:
                print(f"  {alert['status'].upper()}: {alert['message']}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping simulation...")
    finally:
        sensor_simulator.stop_simulation()
        data_logger.stop_logging()