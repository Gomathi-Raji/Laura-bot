"""
IoT Simulation Launcher
======================
Main launcher for the Laura-bot IoT simulation with all virtual components.
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import simulation modules
try:
    from simulation.iot_hardware_sim import iot_manager, gesture_simulator, patch_pyfirmata
    from simulation.sensor_simulation import sensor_simulator, data_logger
    from simulation.gesture_simulator import launch_gesture_simulator
except ImportError as e:
    print(f"❌ Error importing simulation modules: {e}")
    print("Please ensure all simulation files are in the 'simulation' directory")


class IoTSimulationLauncher:
    """Main launcher GUI for IoT simulation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Laura-bot IoT Simulation Launcher")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        # Component status
        self.components = {
            "Hardware Simulator": {"status": "stopped", "process": None, "description": "Mock Arduino & Camera"},
            "Sensor Network": {"status": "stopped", "process": None, "description": "Environmental Sensors"},
            "Gesture Simulator": {"status": "stopped", "process": None, "description": "Virtual Hand Gestures"},
            "IoT Dashboard": {"status": "stopped", "process": None, "description": "Web-based Control Panel"},
            "Voice Assistant": {"status": "stopped", "process": None, "description": "AI Voice Interface"}
        }
        
        self.setup_ui()
        self.update_status()
        
        # Patch pyfirmata for simulation
        try:
            patch_pyfirmata()
            print("✅ Hardware simulation patches applied")
        except Exception as e:
            print(f"⚠️ Warning: Could not apply patches: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title and header
        self.setup_header()
        
        # Component status and controls
        self.setup_component_controls()
        
        # Quick actions
        self.setup_quick_actions()
        
        # Logs and status
        self.setup_logs_section()
        
        # Footer
        self.setup_footer()
    
    def setup_header(self):
        """Setup header section"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🤖 Laura-bot IoT Simulation Platform", 
            font=("Arial", 20, "bold"),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Complete virtual environment for testing IoT features without physical hardware",
            font=("Arial", 11),
            fg='#cccccc',
            bg='#2d2d2d'
        )
        subtitle_label.pack()
    
    def setup_component_controls(self):
        """Setup component control section"""
        components_frame = tk.LabelFrame(
            self.root,
            text="🔧 Simulation Components",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief=tk.RAISED,
            bd=2
        )
        components_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create component controls
        for i, (component, info) in enumerate(self.components.items()):
            self.create_component_control(components_frame, component, info, i)
    
    def create_component_control(self, parent, component_name, component_info, row):
        """Create control panel for a component"""
        
        # Main frame for this component
        comp_frame = tk.Frame(parent, bg='#3d3d3d', relief=tk.RAISED, bd=1)
        comp_frame.pack(fill='x', padx=5, pady=3)
        
        # Component icon and name
        name_frame = tk.Frame(comp_frame, bg='#3d3d3d')
        name_frame.pack(side='left', fill='x', expand=True, padx=10, pady=5)
        
        icon_map = {
            "Hardware Simulator": "🔌",
            "Sensor Network": "🌡️",
            "Gesture Simulator": "👋", 
            "IoT Dashboard": "📊",
            "Voice Assistant": "🎤"
        }
        
        icon = icon_map.get(component_name, "⚙️")
        
        name_label = tk.Label(
            name_frame,
            text=f"{icon} {component_name}",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#3d3d3d'
        )
        name_label.pack(anchor='w')
        
        desc_label = tk.Label(
            name_frame,
            text=component_info["description"],
            font=("Arial", 9),
            fg='#aaaaaa',
            bg='#3d3d3d'
        )
        desc_label.pack(anchor='w')
        
        # Status indicator
        status_frame = tk.Frame(comp_frame, bg='#3d3d3d')
        status_frame.pack(side='right', padx=5, pady=5)
        
        # Status label
        status_var = tk.StringVar(value=component_info["status"].upper())
        setattr(self, f"{component_name}_status_var", status_var)
        
        status_label = tk.Label(
            status_frame,
            textvariable=status_var,
            font=("Arial", 10, "bold"),
            fg=self.get_status_color(component_info["status"]),
            bg='#3d3d3d'
        )
        status_label.pack(side='top')
        
        # Control buttons
        button_frame = tk.Frame(status_frame, bg='#3d3d3d')
        button_frame.pack(side='bottom', pady=2)
        
        start_btn = tk.Button(
            button_frame,
            text="▶️",
            font=("Arial", 8),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            width=3,
            command=lambda: self.start_component(component_name)
        )
        start_btn.pack(side='left', padx=1)
        
        stop_btn = tk.Button(
            button_frame,
            text="⏹️",
            font=("Arial", 8),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            width=3,
            command=lambda: self.stop_component(component_name)
        )
        stop_btn.pack(side='left', padx=1)
        
        config_btn = tk.Button(
            button_frame,
            text="⚙️",
            font=("Arial", 8),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            width=3,
            command=lambda: self.configure_component(component_name)
        )
        config_btn.pack(side='left', padx=1)
    
    def setup_quick_actions(self):
        """Setup quick action buttons"""
        actions_frame = tk.LabelFrame(
            self.root,
            text="⚡ Quick Actions",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief=tk.RAISED,
            bd=2
        )
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        button_frame = tk.Frame(actions_frame, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        # Quick action buttons
        actions = [
            ("🚀 Start All", self.start_all_components, '#28a745'),
            ("⏹️ Stop All", self.stop_all_components, '#dc3545'),
            ("📊 Open Dashboard", self.open_dashboard, '#007bff'),
            ("👋 Gesture Panel", self.open_gesture_panel, '#17a2b8'),
            ("📁 Open Logs", self.open_logs_folder, '#6c757d'),
            ("❓ Help", self.show_help, '#ffc107')
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 10, "bold"),
                bg=color,
                fg='white',
                relief=tk.RAISED,
                bd=2,
                padx=15,
                pady=5,
                command=command
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=3, sticky='ew')
        
        # Configure grid weights
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
    
    def setup_logs_section(self):
        """Setup logs and status section"""
        logs_frame = tk.LabelFrame(
            self.root,
            text="📜 Activity Log",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief=tk.RAISED,
            bd=2
        )
        logs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(logs_frame, bg='#2d2d2d')
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(
            text_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9),
            wrap=tk.WORD,
            height=8
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Clear log button
        clear_btn = tk.Button(
            logs_frame,
            text="🗑️ Clear Log",
            font=("Arial", 9),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            command=self.clear_log
        )
        clear_btn.pack(side='bottom', pady=3)
        
        # Initial log entries
        self.log_message("🚀 IoT Simulation Launcher initialized")
        self.log_message("💡 Use Quick Actions to start components")
    
    def setup_footer(self):
        """Setup footer section"""
        footer_frame = tk.Frame(self.root, bg='#2d2d2d', height=50)
        footer_frame.pack(fill='x', padx=10, pady=5)
        footer_frame.pack_propagate(False)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to launch IoT simulation")
        status_label = tk.Label(
            footer_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg='#cccccc',
            bg='#2d2d2d'
        )
        status_label.pack(side='left', pady=15)
        
        # Exit button
        exit_btn = tk.Button(
            footer_frame,
            text="❌ Exit",
            font=("Arial", 10, "bold"),
            bg='#dc3545',
            fg='white',
            relief=tk.RAISED,
            bd=2,
            command=self.exit_application
        )
        exit_btn.pack(side='right', pady=10)
    
    def get_status_color(self, status):
        """Get color for status"""
        colors = {
            "stopped": "#dc3545",
            "starting": "#ffc107",
            "running": "#28a745",
            "error": "#dc3545"
        }
        return colors.get(status, "#6c757d")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("📋 Log cleared")
    
    def start_component(self, component_name):
        """Start a specific component"""
        try:
            self.log_message(f"🚀 Starting {component_name}...")
            
            if component_name == "Hardware Simulator":
                # Already initialized with imports
                self.components[component_name]["status"] = "running"
                self.log_message("✅ Hardware simulator ready")
                
            elif component_name == "Sensor Network":
                sensor_simulator.start_simulation()
                data_logger.start_logging()
                self.components[component_name]["status"] = "running"
                self.log_message("✅ Sensor network started")
                
            elif component_name == "Gesture Simulator":
                # Launch in separate thread
                threading.Thread(
                    target=launch_gesture_simulator,
                    daemon=True
                ).start()
                self.components[component_name]["status"] = "running"
                self.log_message("✅ Gesture simulator launched")
                
            elif component_name == "IoT Dashboard":
                # Launch Streamlit dashboard
                dashboard_cmd = [
                    sys.executable, "-m", "streamlit", "run", 
                    "simulation/iot_dashboard.py",
                    "--server.headless", "true"
                ]
                process = subprocess.Popen(
                    dashboard_cmd,
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.components[component_name]["process"] = process
                self.components[component_name]["status"] = "running"
                self.log_message("✅ IoT dashboard started")
                
                # Open in browser after delay
                threading.Timer(3.0, lambda: webbrowser.open("http://localhost:8501")).start()
                
            elif component_name == "Voice Assistant":
                # Launch main voice assistant
                assistant_cmd = [sys.executable, "main.py"]
                process = subprocess.Popen(
                    assistant_cmd,
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.components[component_name]["process"] = process
                self.components[component_name]["status"] = "running"
                self.log_message("✅ Voice assistant started")
            
            self.update_component_status(component_name)
            self.status_var.set(f"{component_name} started successfully")
            
        except Exception as e:
            self.log_message(f"❌ Error starting {component_name}: {e}")
            self.components[component_name]["status"] = "error"
            self.update_component_status(component_name)
    
    def stop_component(self, component_name):
        """Stop a specific component"""
        try:
            self.log_message(f"⏹️ Stopping {component_name}...")
            
            if component_name == "Sensor Network":
                sensor_simulator.stop_simulation()
                data_logger.stop_logging()
                
            # Kill process if exists
            if self.components[component_name]["process"]:
                self.components[component_name]["process"].terminate()
                self.components[component_name]["process"] = None
            
            self.components[component_name]["status"] = "stopped"
            self.update_component_status(component_name)
            self.log_message(f"✅ {component_name} stopped")
            self.status_var.set(f"{component_name} stopped")
            
        except Exception as e:
            self.log_message(f"❌ Error stopping {component_name}: {e}")
    
    def configure_component(self, component_name):
        """Configure a specific component"""
        config_info = {
            "Hardware Simulator": "Mock Arduino on COM7, Virtual camera simulation",
            "Sensor Network": "10 sensors: temp, humidity, air quality, motion, etc.",
            "Gesture Simulator": "Hand gesture recognition: Hi, Ambulance, Fire, etc.",
            "IoT Dashboard": "Web interface at http://localhost:8501",
            "Voice Assistant": "Tamil/English voice commands with AI responses"
        }
        
        info = config_info.get(component_name, "No configuration available")
        messagebox.showinfo(f"{component_name} Configuration", info)
    
    def start_all_components(self):
        """Start all components"""
        self.log_message("🚀 Starting all components...")
        
        for component in self.components.keys():
            if self.components[component]["status"] != "running":
                self.start_component(component)
                time.sleep(1)  # Stagger starts
        
        self.status_var.set("All components started")
    
    def stop_all_components(self):
        """Stop all components"""
        self.log_message("⏹️ Stopping all components...")
        
        for component in self.components.keys():
            if self.components[component]["status"] == "running":
                self.stop_component(component)
        
        self.status_var.set("All components stopped")
    
    def open_dashboard(self):
        """Open IoT dashboard in browser"""
        webbrowser.open("http://localhost:8501")
        self.log_message("🌐 Opening IoT dashboard in browser")
    
    def open_gesture_panel(self):
        """Open gesture control panel"""
        try:
            threading.Thread(target=launch_gesture_simulator, daemon=True).start()
            self.log_message("👋 Gesture control panel launched")
        except Exception as e:
            self.log_message(f"❌ Error launching gesture panel: {e}")
    
    def open_logs_folder(self):
        """Open logs folder"""
        logs_path = os.path.join(project_root, "simulation")
        if os.path.exists(logs_path):
            os.startfile(logs_path)
            self.log_message("📁 Opened simulation folder")
        else:
            self.log_message("❌ Simulation folder not found")
    
    def show_help(self):
        """Show help information"""
        help_text = """
🤖 Laura-bot IoT Simulation Help

Components:
• Hardware Simulator: Mock Arduino & Camera
• Sensor Network: Environmental monitoring
• Gesture Simulator: Virtual hand gestures  
• IoT Dashboard: Web-based control panel
• Voice Assistant: AI voice interface

Quick Start:
1. Click "Start All" to launch everything
2. Open Dashboard for monitoring
3. Use Gesture Panel for interaction
4. Check Activity Log for status

Controls:
▶️ Start component
⏹️ Stop component  
⚙️ Component info

For more help, check README.md
        """
        messagebox.showinfo("Help", help_text.strip())
    
    def update_component_status(self, component_name):
        """Update component status display"""
        status_var = getattr(self, f"{component_name}_status_var")
        status = self.components[component_name]["status"]
        status_var.set(status.upper())
    
    def update_status(self):
        """Update all component statuses"""
        for component_name in self.components.keys():
            status_var = getattr(self, f"{component_name}_status_var", None)
            if status_var:
                status = self.components[component_name]["status"]
                status_var.set(status.upper())
        
        # Schedule next update
        self.root.after(5000, self.update_status)
    
    def exit_application(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Stop all components and exit?"):
            self.log_message("⏹️ Shutting down all components...")
            self.stop_all_components()
            time.sleep(1)
            self.root.quit()
    
    def run(self):
        """Run the launcher"""
        self.log_message("🎮 IoT Simulation Launcher ready")
        self.status_var.set("Ready - Select components to start")
        self.root.mainloop()


def main():
    """Main function"""
    print("🚀 Starting Laura-bot IoT Simulation Launcher...")
    
    try:
        launcher = IoTSimulationLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ Error starting launcher: {e}")
        messagebox.showerror("Error", f"Failed to start launcher:\n\n{e}")


if __name__ == "__main__":
    main()