#!/usr/bin/env python3

print("🤖 LAURA-BOT WEB APPLICATION STARTUP")
print("=" * 50)

import sys
import os
from datetime import datetime

print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📁 Directory: {os.getcwd()}")

# Test Flask import
try:
    from flask import Flask
    from flask_socketio import SocketIO
    print("✅ Flask and SocketIO are available")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Create and test app
try:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    socketio = SocketIO(app)
    
    @app.route('/')
    def home():
        return '''
        <h1>🤖 Laura-bot is RUNNING!</h1>
        <p>Server Status: ✅ ONLINE</p>
        <p>Time: ''' + datetime.now().strftime('%H:%M:%S') + '''</p>
        <h2>Available Features:</h2>
        <ul>
            <li><a href="/api/test">🔧 API Test</a></li>
            <li><a href="/learn">📚 Learning Module</a></li>
            <li><a href="/quiz">🧠 Quiz System</a></li>
            <li><a href="/progress">📈 Progress Analytics</a></li>
        </ul>
        '''
    
    @app.route('/api/test')
    def test():
        return {
            'status': 'SUCCESS',
            'message': 'Laura-bot API is working!',
            'timestamp': datetime.now().isoformat()
        }
    
    print("✅ Flask app configured successfully")
    print("\n🚀 STARTING SERVER...")
    print("📍 URL: http://localhost:5555")
    print("🎯 Open your browser to see Laura-bot!")
    print("=" * 50)
    
    # Start server
    socketio.run(app, host='0.0.0.0', port=5555, debug=False)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()