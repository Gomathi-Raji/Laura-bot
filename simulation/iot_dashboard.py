"""
IoT Dashboard Interface
======================
Comprehensive Streamlit dashboard for monitoring and controlling the Laura-bot IoT simulation.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
import threading

# Import simulation modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simulation.iot_hardware_sim import iot_manager, gesture_simulator
    from simulation.sensor_simulation import sensor_simulator, data_logger
except ImportError:
    st.error("⚠️ Could not import simulation modules. Please ensure all simulation files are present.")
    st.stop()


class IoTDashboard:
    """Main IoT dashboard class"""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="🤖 Laura-bot IoT Simulation Dashboard",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .alert-critical {
            background-color: #fee;
            border-left: 4px solid #dc3545;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        .alert-warning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        .status-online {
            color: #28a745;
            font-weight: bold;
        }
        .status-offline {
            color: #dc3545;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'dashboard_started' not in st.session_state:
            st.session_state.dashboard_started = False
        if 'simulation_running' not in st.session_state:
            st.session_state.simulation_running = False
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
    
    def render_header(self):
        """Render dashboard header"""
        st.markdown("""
        <div class="main-header">
            <h1>🤖 Laura-bot IoT Simulation Dashboard</h1>
            <p>Real-time monitoring and control of virtual IoT devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.title("🎛️ Control Panel")
        
        # Simulation control
        st.sidebar.subheader("🚀 Simulation Control")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("▶️ Start Simulation", key="start_sim"):
                self.start_simulation()
        
        with col2:
            if st.button("⏹️ Stop Simulation", key="stop_sim"):
                self.stop_simulation()
        
        # Auto-refresh toggle
        st.session_state.auto_refresh = st.sidebar.checkbox(
            "🔄 Auto Refresh (5s)", 
            value=st.session_state.auto_refresh
        )
        
        # Manual refresh
        if st.sidebar.button("🔃 Refresh Now"):
            st.rerun()
        
        # Gesture simulation controls
        st.sidebar.subheader("👋 Gesture Simulator")
        
        available_gestures = gesture_simulator.get_available_gestures()
        selected_gesture = st.sidebar.selectbox(
            "Select Gesture:",
            ["None"] + available_gestures
        )
        
        if st.sidebar.button("🎯 Trigger Gesture") and selected_gesture != "None":
            gesture_simulator.simulate_gesture(selected_gesture)
            st.sidebar.success(f"Triggered: {selected_gesture}")
        
        # Device control
        st.sidebar.subheader("🔧 Device Control")
        
        device_names = ["arduino_main", "camera", "sensors"]
        selected_device = st.sidebar.selectbox("Select Device:", device_names)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("❌ Simulate Failure"):
                iot_manager.simulate_device_failure(selected_device)
                st.sidebar.warning(f"Simulated {selected_device} failure")
        
        with col2:
            if st.button("✅ Restore Device"):
                iot_manager.restore_device(selected_device)
                st.sidebar.success(f"Restored {selected_device}")
        
        # Export data
        st.sidebar.subheader("📊 Data Export")
        if st.sidebar.button("💾 Export Sensor Data"):
            self.export_sensor_data()
    
    def start_simulation(self):
        """Start the IoT simulation"""
        try:
            sensor_simulator.start_simulation()
            data_logger.start_logging()
            st.session_state.simulation_running = True
            st.sidebar.success("✅ Simulation started!")
        except Exception as e:
            st.sidebar.error(f"❌ Error starting simulation: {e}")
    
    def stop_simulation(self):
        """Stop the IoT simulation"""
        try:
            sensor_simulator.stop_simulation()
            data_logger.stop_logging()
            st.session_state.simulation_running = False
            st.sidebar.success("⏹️ Simulation stopped!")
        except Exception as e:
            st.sidebar.error(f"❌ Error stopping simulation: {e}")
    
    def render_overview_metrics(self):
        """Render overview metrics"""
        st.subheader("📊 System Overview")
        
        # Get device status
        device_status = iot_manager.get_device_status()
        sensor_stats = sensor_simulator.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            arduino_connected = device_status["arduino_main"]["connected"]
            status_text = "Online" if arduino_connected else "Offline"
            status_color = "normal" if arduino_connected else "inverse"
            st.metric(
                "🔌 Arduino Status",
                status_text,
                delta=None,
                delta_color=status_color
            )
        
        with col2:
            camera_active = device_status["camera"]["active"]
            status_text = "Active" if camera_active else "Inactive"
            st.metric(
                "📹 Camera Status",
                status_text,
                delta=device_status["camera"]["current_gesture"]
            )
        
        with col3:
            st.metric(
                "🌡️ Active Sensors",
                f"{sensor_stats['active_sensors']}/{sensor_stats['total_sensors']}",
                delta=f"{sensor_stats['total_readings']} readings"
            )
        
        with col4:
            total_alerts = sensor_stats['critical_alerts'] + sensor_stats['warning_alerts']
            st.metric(
                "🚨 Total Alerts",
                total_alerts,
                delta=f"{sensor_stats['critical_alerts']} critical"
            )
    
    def render_sensor_monitoring(self):
        """Render sensor monitoring section"""
        st.subheader("🌡️ Sensor Monitoring")
        
        # Get current sensor readings
        try:
            readings = sensor_simulator.get_current_readings()
            
            if not readings:
                st.warning("⚠️ No sensor data available. Start the simulation to see data.")
                return
            
            # Create DataFrame
            sensor_data = []
            for reading in readings:
                sensor_data.append({
                    "Sensor ID": reading.sensor_id,
                    "Type": reading.sensor_type.replace("_", " ").title(),
                    "Location": reading.location.replace("_", " ").title(),
                    "Value": f"{reading.value} {reading.unit}",
                    "Status": reading.status.title(),
                    "Timestamp": datetime.fromisoformat(reading.timestamp).strftime("%H:%M:%S")
                })
            
            df = pd.DataFrame(sensor_data)
            
            # Color code by status
            def color_status(val, col_name):
                if col_name == "Status":
                    if val == "Critical":
                        return "background-color: #fee; color: #721c24"
                    elif val == "Warning":
                        return "background-color: #fff3cd; color: #856404"
                    else:
                        return "background-color: #d4edda; color: #155724"
                return ""
            
            styled_df = df.style.applymap(lambda x: color_status(x, "Status") if x in ["Critical", "Warning", "Normal"] else "", subset=["Status"])
            
            st.dataframe(styled_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error loading sensor data: {e}")
    
    def render_sensor_charts(self):
        """Render sensor data visualization"""
        st.subheader("📈 Sensor Data Visualization")
        
        try:
            readings = sensor_simulator.get_current_readings()
            
            if not readings:
                st.info("📊 Start simulation to see sensor charts")
                return
            
            # Group sensors by type
            sensor_types = {}
            for reading in readings:
                if reading.sensor_type not in sensor_types:
                    sensor_types[reading.sensor_type] = []
                sensor_types[reading.sensor_type].append(reading)
            
            # Create charts for each sensor type
            for sensor_type, type_readings in sensor_types.items():
                if len(type_readings) > 1:
                    # Multiple sensors of same type - bar chart
                    fig = px.bar(
                        x=[r.location for r in type_readings],
                        y=[r.value for r in type_readings],
                        title=f"{sensor_type.replace('_', ' ').title()} by Location",
                        color=[r.status for r in type_readings],
                        color_discrete_map={
                            "normal": "#28a745",
                            "warning": "#ffc107", 
                            "critical": "#dc3545"
                        }
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Single sensor - gauge chart
                    reading = type_readings[0]
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=reading.value,
                        title={"text": f"{sensor_type.replace('_', ' ').title()} ({reading.location})"},
                        domain={"x": [0, 1], "y": [0, 1]},
                        gauge={
                            "axis": {"range": [None, reading.value * 2]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, reading.value * 0.7], "color": "lightgray"},
                                {"range": [reading.value * 0.7, reading.value * 1.3], "color": "gray"}
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": reading.value * 1.2
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error creating charts: {e}")
    
    def render_alerts_section(self):
        """Render alerts and notifications"""
        st.subheader("🚨 Alerts & Notifications")
        
        try:
            alerts = sensor_simulator.get_alerts(limit=20)
            
            if not alerts:
                st.success("✅ No alerts - all systems normal")
                return
            
            # Separate by severity
            critical_alerts = [a for a in alerts if a["status"] == "critical"]
            warning_alerts = [a for a in alerts if a["status"] == "warning"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("🚨 **Critical Alerts**")
                if critical_alerts:
                    for alert in critical_alerts[-5:]:
                        st.markdown(f"""
                        <div class="alert-critical">
                            <strong>{alert['sensor_type'].replace('_', ' ').title()}</strong><br>
                            {alert['message']}<br>
                            <small>{datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No critical alerts")
            
            with col2:
                st.write("⚠️ **Warning Alerts**")
                if warning_alerts:
                    for alert in warning_alerts[-5:]:
                        st.markdown(f"""
                        <div class="alert-warning">
                            <strong>{alert['sensor_type'].replace('_', ' ').title()}</strong><br>
                            {alert['message']}<br>
                            <small>{datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No warning alerts")
                    
        except Exception as e:
            st.error(f"❌ Error loading alerts: {e}")
    
    def render_device_status(self):
        """Render device status section"""
        st.subheader("🔧 Device Status")
        
        try:
            device_status = iot_manager.get_device_status()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**🔌 Arduino Main**")
                arduino = device_status["arduino_main"]
                status_class = "status-online" if arduino["connected"] else "status-offline"
                st.markdown(f'Status: <span class="{status_class}">{"Connected" if arduino["connected"] else "Disconnected"}</span>', unsafe_allow_html=True)
                st.write(f"Port: {arduino['port']}")
                st.write(f"Uptime: {arduino['uptime']}s")
            
            with col2:
                st.write("**📹 Camera System**")
                camera = device_status["camera"]
                status_class = "status-online" if camera["active"] else "status-offline"
                st.markdown(f'Status: <span class="{status_class}">{"Active" if camera["active"] else "Inactive"}</span>', unsafe_allow_html=True)
                st.write(f"Source: {camera['source']}")
                st.write(f"Current Gesture: {camera['current_gesture']}")
            
            with col3:
                st.write("**🌡️ Sensor Network**")
                sensors = device_status["sensors"]
                st.markdown('<span class="status-online">Active</span>', unsafe_allow_html=True)
                st.write(f"Temperature: {sensors['data']['temperature']}°C")
                st.write(f"Humidity: {sensors['data']['humidity']}%")
                st.write(f"Last Update: {datetime.fromisoformat(sensors['last_update']).strftime('%H:%M:%S')}")
                
        except Exception as e:
            st.error(f"❌ Error loading device status: {e}")
    
    def export_sensor_data(self):
        """Export sensor data to JSON"""
        try:
            readings = sensor_simulator.get_current_readings()
            alerts = sensor_simulator.get_alerts()
            stats = sensor_simulator.get_statistics()
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "readings": [
                    {
                        "sensor_id": r.sensor_id,
                        "sensor_type": r.sensor_type,
                        "value": r.value,
                        "unit": r.unit,
                        "location": r.location,
                        "status": r.status,
                        "timestamp": r.timestamp
                    } for r in readings
                ],
                "alerts": alerts,
                "statistics": stats
            }
            
            # Convert to JSON string
            json_data = json.dumps(export_data, indent=2)
            
            # Provide download
            st.download_button(
                label="📥 Download Sensor Data",
                data=json_data,
                file_name=f"iot_sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Error exporting data: {e}")
    
    def run(self):
        """Run the dashboard"""
        self.render_header()
        self.render_sidebar()
        
        # Main content
        self.render_overview_metrics()
        st.divider()
        
        # Two column layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_sensor_monitoring()
            st.divider()
            self.render_sensor_charts()
        
        with col2:
            self.render_device_status()
            st.divider()
            self.render_alerts_section()
        
        # Auto-refresh
        if st.session_state.auto_refresh:
            time.sleep(5)
            st.rerun()


def main():
    """Main function to run the dashboard"""
    dashboard = IoTDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()