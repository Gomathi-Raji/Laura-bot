"""
Zara Voice Assistant Launcher
Choose between different interface modes
"""

import subprocess
import sys
import os

def run_original_app():
    """Run the original terminal-based app"""
    print("🤖 Starting Zara Voice Assistant (Terminal Mode)...")
    subprocess.run([sys.executable, "main.py"])

def run_streamlit_ui():
    """Run the Streamlit web UI"""
    print("🌐 Starting Zara Voice Assistant (Web UI)...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_ui.py", "--server.port", "8501"])

def main():
    print("=" * 50)
    print("🤖 ZARA VOICE ASSISTANT LAUNCHER")
    print("=" * 50)
    print("\nChoose your interface:")
    print("1. 💻 Terminal Mode (Original)")
    print("2. 🌐 Web UI (Streamlit)")
    print("3. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_original_app()
            break
        elif choice == "2":
            run_streamlit_ui()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
