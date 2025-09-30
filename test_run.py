#!/usr/bin/env python3
"""
Test script to run the Laura-bot Flask application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🚀 Starting Laura-bot Flask Application Test")
    print("=" * 50)
    
    # Import the Flask app
    from working_app import app, socketio
    
    print("✅ Flask app imported successfully")
    print("🌐 Starting server on http://localhost:5555")
    print("🤖 Available routes:")
    print("   - / (Enhanced Dashboard)")
    print("   - /learn (Interactive Learning)")
    print("   - /quiz (Quiz System)")
    print("   - /progress (Progress Analytics)")
    print("   - /hardware (Hardware Control)")
    print("=" * 50)
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
    
except Exception as e:
    print(f"❌ Error starting Laura-bot: {e}")
    print("🔍 Error details:")
    import traceback
    traceback.print_exc()
    
finally:
    print("🛑 Laura-bot server stopped")