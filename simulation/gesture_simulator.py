"""
Virtual Gesture Control Panel
============================
Interactive GUI for simulating hand gestures without physical camera input.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
from simulation.iot_hardware_sim import iot_manager, gesture_simulator


class GestureControlPanel:
    """GUI control panel for gesture simulation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤲 Laura-bot Gesture Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Gesture callbacks
        self.gesture_callbacks = []
        
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="🤲 Virtual Gesture Simulator", 
            font=("Arial", 20, "bold"),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack()
        
        # Status frame
        self.setup_status_frame()
        
        # Gesture buttons frame
        self.setup_gesture_frame()
        
        # Hand position visualizer
        self.setup_hand_visualizer()
        
        # Control buttons
        self.setup_control_frame()
    
    def setup_status_frame(self):
        """Setup status display frame"""
        status_frame = tk.LabelFrame(
            self.root, 
            text="📊 System Status", 
            font=("Arial", 12, "bold"),
            fg='#ecf0f1',
            bg='#34495e',
            relief=tk.RAISED,
            bd=2
        )
        status_frame.pack(pady=10, padx=20, fill='x')
        
        # Current gesture display
        self.current_gesture_var = tk.StringVar(value="Unknown")
        gesture_label = tk.Label(
            status_frame,
            text="Current Gesture:",
            font=("Arial", 10, "bold"),
            fg='#ecf0f1',
            bg='#34495e'
        )
        gesture_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.gesture_display = tk.Label(
            status_frame,
            textvariable=self.current_gesture_var,
            font=("Arial", 12, "bold"),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.gesture_display.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Camera status
        self.camera_status_var = tk.StringVar(value="Active")
        camera_label = tk.Label(
            status_frame,
            text="Camera Status:",
            font=("Arial", 10, "bold"),
            fg='#ecf0f1',
            bg='#34495e'
        )
        camera_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.camera_display = tk.Label(
            status_frame,
            textvariable=self.camera_status_var,
            font=("Arial", 10),
            fg='#27ae60',
            bg='#34495e'
        )
        self.camera_display.grid(row=1, column=1, sticky='w', padx=10, pady=5)
    
    def setup_gesture_frame(self):
        """Setup gesture control buttons"""
        gesture_frame = tk.LabelFrame(
            self.root,
            text="👋 Gesture Controls",
            font=("Arial", 12, "bold"),
            fg='#ecf0f1',
            bg='#34495e',
            relief=tk.RAISED,
            bd=2
        )
        gesture_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Create gesture buttons in a grid
        gestures = gesture_simulator.get_available_gestures()
        colors = [
            '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
            '#e67e22', '#1abc9c', '#34495e', '#95a5a6', '#16a085'
        ]
        
        for i, gesture in enumerate(gestures):
            row = i // 3
            col = i % 3
            color = colors[i % len(colors)]
            
            btn = tk.Button(
                gesture_frame,
                text=f"{gesture}\n{self.get_gesture_description(gesture)}",
                font=("Arial", 10, "bold"),
                bg=color,
                fg='white',
                activebackground=self.darken_color(color),
                relief=tk.RAISED,
                bd=3,
                width=15,
                height=3,
                command=lambda g=gesture: self.trigger_gesture(g)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Configure grid weights
        for i in range(3):
            gesture_frame.columnconfigure(i, weight=1)
    
    def setup_hand_visualizer(self):
        """Setup hand position visualizer"""
        viz_frame = tk.LabelFrame(
            self.root,
            text="✋ Hand Position Visualizer",
            font=("Arial", 12, "bold"),
            fg='#ecf0f1',
            bg='#34495e',
            relief=tk.RAISED,
            bd=2
        )
        viz_frame.pack(pady=10, padx=20, fill='x')
        
        # Canvas for hand visualization
        self.hand_canvas = tk.Canvas(
            viz_frame,
            width=400,
            height=200,
            bg='#2c3e50',
            highlightthickness=0
        )
        self.hand_canvas.pack(pady=10)
        
        self.draw_default_hands()
    
    def setup_control_frame(self):
        """Setup control buttons"""
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=10)
        
        # Random gesture button
        random_btn = tk.Button(
            control_frame,
            text="🎲 Random Gesture",
            font=("Arial", 10, "bold"),
            bg='#8e44ad',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            command=self.random_gesture
        )
        random_btn.pack(side=tk.LEFT, padx=10)
        
        # Clear gesture button
        clear_btn = tk.Button(
            control_frame,
            text="🧹 Clear Gesture",
            font=("Arial", 10, "bold"),
            bg='#95a5a6',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            command=self.clear_gesture
        )
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Emergency simulation
        emergency_btn = tk.Button(
            control_frame,
            text="🚨 Emergency Mode",
            font=("Arial", 10, "bold"),
            bg='#c0392b',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            command=self.emergency_sequence
        )
        emergency_btn.pack(side=tk.LEFT, padx=10)
    
    def get_gesture_description(self, gesture):
        """Get description for gesture"""
        descriptions = {
            "Hi": "👋 Greeting",
            "Ambulance": "🚑 Medical Help",
            "Fire": "🔥 Fire Emergency",
            "Sick": "🤒 Health Issue",
            "Water": "💧 Need Water",
            "Up": "⬆️ Move Up",
            "Down": "⬇️ Move Down",
            "Danger": "⚠️ Warning",
            "Stop": "✋ Stop Action",
            "Wait": "⏸️ Wait/Pause"
        }
        return descriptions.get(gesture, "❓ Unknown")
    
    def darken_color(self, color):
        """Darken a hex color for button hover effect"""
        # Simple darkening by reducing hex values
        if color.startswith('#'):
            r = max(0, int(color[1:3], 16) - 30)
            g = max(0, int(color[3:5], 16) - 30)
            b = max(0, int(color[5:7], 16) - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def draw_default_hands(self):
        """Draw default hand positions"""
        self.hand_canvas.delete("all")
        
        # Left hand
        self.draw_hand(100, 100, "left", "00000")
        
        # Right hand  
        self.draw_hand(300, 100, "right", "00000")
        
        # Labels
        self.hand_canvas.create_text(100, 180, text="Left Hand", fill='#ecf0f1', font=("Arial", 10, "bold"))
        self.hand_canvas.create_text(300, 180, text="Right Hand", fill='#ecf0f1', font=("Arial", 10, "bold"))
    
    def draw_hand(self, x, y, hand_type, finger_pattern):
        """Draw a hand with finger positions"""
        # Hand base (palm)
        self.hand_canvas.create_oval(x-30, y-20, x+30, y+40, fill='#f39c12', outline='#e67e22', width=2)
        
        # Fingers (thumb, index, middle, ring, pinky)
        finger_positions = [
            (-25, -10), (-10, -30), (0, -35), (10, -30), (25, -10)
        ]
        
        for i, (fx, fy) in enumerate(finger_positions):
            finger_state = int(finger_pattern[i]) if i < len(finger_pattern) else 0
            color = '#27ae60' if finger_state else '#e74c3c'
            
            # Draw finger
            self.hand_canvas.create_oval(
                x + fx - 5, y + fy - 10,
                x + fx + 5, y + fy + 10,
                fill=color, outline='#2c3e50', width=1
            )
    
    def trigger_gesture(self, gesture_name):
        """Trigger a specific gesture"""
        gesture_simulator.simulate_gesture(gesture_name)
        self.current_gesture_var.set(gesture_name)
        
        # Update hand visualization
        if gesture_name in gesture_simulator.gesture_map:
            left_pattern, right_pattern = gesture_simulator.gesture_map[gesture_name]
            self.hand_canvas.delete("all")
            self.draw_hand(100, 100, "left", left_pattern)
            self.draw_hand(300, 100, "right", right_pattern)
            self.hand_canvas.create_text(100, 180, text="Left Hand", fill='#ecf0f1', font=("Arial", 10, "bold"))
            self.hand_canvas.create_text(300, 180, text="Right Hand", fill='#ecf0f1', font=("Arial", 10, "bold"))
        
        # Flash the interface
        self.flash_interface()
        
        # Log the gesture
        print(f"🎯 Gesture triggered from GUI: {gesture_name}")
    
    def random_gesture(self):
        """Trigger a random gesture"""
        import random
        gestures = gesture_simulator.get_available_gestures()
        random_gesture = random.choice(gestures)
        self.trigger_gesture(random_gesture)
    
    def clear_gesture(self):
        """Clear current gesture"""
        self.current_gesture_var.set("Unknown")
        self.draw_default_hands()
        gesture_simulator.current_gesture = "Unknown"
    
    def emergency_sequence(self):
        """Simulate emergency gesture sequence"""
        emergency_gestures = ["Ambulance", "Fire", "Sick", "Danger"]
        
        def run_sequence():
            for gesture in emergency_gestures:
                self.trigger_gesture(gesture)
                time.sleep(2)
        
        threading.Thread(target=run_sequence, daemon=True).start()
    
    def flash_interface(self):
        """Flash the interface to indicate gesture activation"""
        original_bg = self.root.cget('bg')
        self.root.configure(bg='#27ae60')
        self.root.after(200, lambda: self.root.configure(bg=original_bg))
    
    def update_status(self):
        """Update status display"""
        status = iot_manager.get_device_status()
        camera_active = status['camera']['active']
        self.camera_status_var.set("Active" if camera_active else "Inactive")
        self.camera_display.configure(fg='#27ae60' if camera_active else '#e74c3c')
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def run(self):
        """Start the gesture control panel"""
        print("🎮 Starting Virtual Gesture Control Panel...")
        self.root.mainloop()


def launch_gesture_simulator():
    """Launch the gesture simulator"""
    try:
        panel = GestureControlPanel()
        panel.run()
    except Exception as e:
        print(f"❌ Error launching gesture simulator: {e}")
        messagebox.showerror("Error", f"Failed to launch gesture simulator:\n{e}")


if __name__ == "__main__":
    launch_gesture_simulator()