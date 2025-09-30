#!/usr/bin/env python3
"""
Laura-bot Flask Application - Non-blocking startup
"""

import sys
import os
import threading
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'laura-bot-secret-key-2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Main routes
@app.route('/')
def dashboard():
    try:
        return render_template('enhanced_dashboard.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Laura-bot Dashboard</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    text-align: center; 
                }}
                .container {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }}
                h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
                a {{ color: #ffeb3b; margin: 10px; display: inline-block; padding: 10px 20px; 
                     background: rgba(255,255,255,0.1); border-radius: 5px; text-decoration: none; }}
                a:hover {{ background: rgba(255,255,255,0.2); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Laura-bot Educational Platform</h1>
                <p>Welcome to your intelligent learning companion!</p>
                
                <h2>Quick Access:</h2>
                <a href="/learn">Interactive Learning</a>
                <a href="/quiz">Quiz System</a>
                <a href="/progress">Progress Analytics</a>
                <a href="/hardware">Hardware Control</a>
                <a href="/api/test">Test API</a>
                
                <div style="margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                    <h3>Server Status</h3>
                    <p>Server: Running on http://localhost:5555</p>
                    <p>Template Status: Using fallback (templates found: {os.path.exists('templates')})</p>
                    <p>Time: <script>document.write(new Date().toLocaleString())</script></p>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/learn')
def interactive_learning():
    try:
        return render_template('interactive_learning.html')
    except:
        return '<h1>Interactive Learning Module</h1><p>Coming soon!</p><a href="/">Back to Dashboard</a>'

@app.route('/quiz')
def quiz_interface():
    try:
        return render_template('quiz.html')
    except:
        return '<h1>Quiz System</h1><p>Coming soon!</p><a href="/">Back to Dashboard</a>'

@app.route('/progress')
def progress():
    try:
        return render_template('progress_analytics.html')
    except:
        return '<h1>Progress Analytics</h1><p>Coming soon!</p><a href="/">Back to Dashboard</a>'

@app.route('/hardware')
def hardware_control():
    try:
        return render_template('hardware_control.html')
    except:
        return '<h1>Hardware Control</h1><p>Coming soon!</p><a href="/">Back to Dashboard</a>'

# API routes
@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'Laura-bot API is working!',
        'server': 'Flask + SocketIO',
        'timestamp': time.time(),
        'features': ['Learning', 'Quiz', 'Progress', 'Hardware']
    })

@app.route('/api/progress_data')
def progress_data():
    return jsonify({
        'success': True,
        'stats': {
            'total_sessions': 15,
            'study_time_hours': 28.5,
            'avg_quiz_score': 89,
            'current_streak': 8,
            'subjects_mastered': 3
        },
        'recent_activity': [
            {'subject': 'Mathematics', 'score': 92, 'date': '2024-01-15'},
            {'subject': 'Science', 'score': 87, 'date': '2024-01-14'},
            {'subject': 'History', 'score': 94, 'date': '2024-01-13'}
        ]
    })

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print('Client connected to Laura-bot')
    emit('status_update', {
        'message': 'Connected to Laura-bot successfully!',
        'timestamp': time.time(),
        'server_status': 'online'
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from Laura-bot')

@socketio.on('request_status')
def handle_status_request():
    emit('status_update', {
        'message': 'Laura-bot is running normally',
        'timestamp': time.time(),
        'server_status': 'online',
        'active_features': ['Learning', 'Quiz', 'Progress', 'Hardware']
    })

def run_server():
    """Run the Flask-SocketIO server"""
    try:
        print("Laura-bot Flask Server Starting...")
        print("URL: http://localhost:5555")
        print("Available routes:")
        print("  - Dashboard: http://localhost:5555/")
        print("  - Learning: http://localhost:5555/learn")
        print("  - Quiz: http://localhost:5555/quiz")
        print("  - Progress: http://localhost:5555/progress")
        print("  - Hardware: http://localhost:5555/hardware")
        print("  - API Test: http://localhost:5555/api/test")
        print("Press Ctrl+C in your browser or close this window to stop")
        
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5555, 
            debug=False,  # Disable debug to prevent reloader issues
            allow_unsafe_werkzeug=True,
            use_reloader=False  # Disable reloader
        )
        
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_server()