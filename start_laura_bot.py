#!/usr/bin/env python3
"""
Laura-bot Startup Script
Starts the Flask application with proper error handling
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_port_available(port):
    """Check if port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def start_laura_bot():
    """Start Laura-bot Flask application"""
    print("🚀 Starting Laura-bot AI Learning Assistant")
    print("=" * 50)
    
    try:
        # Import the Flask app
        from flask_app import app, socketio
        
        # Check if port 5000 is available
        port = 5000
        if not check_port_available(port):
            print(f"⚠️ Port {port} is busy, trying port 5001...")
            port = 5001
            if not check_port_available(port):
                print(f"⚠️ Port {port} is also busy, using port 5002...")
                port = 5002
        
        print(f"✅ Starting server on port {port}")
        print(f"🌐 Access Laura-bot at: http://localhost:{port}")
        print(f"📱 Mobile users will get the mobile-optimized interface")
        print(f"🤖 Hardware: {'Connected' if os.environ.get('HARDWARE_CONNECTED') == 'true' else 'Simulation Mode'}")
        print(f"🧠 AI: {'Available' if os.environ.get('AI_AVAILABLE') == 'true' else 'Fallback Mode'}")
        print("-" * 50)
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the Flask-SocketIO server
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=port, 
            debug=True,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Laura-bot server stopped by user")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Please install required dependencies:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Server Error: {e}")
        print("🔧 Check the logs above for more details")

if __name__ == "__main__":
    start_laura_bot()