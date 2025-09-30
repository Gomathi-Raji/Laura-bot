#!/usr/bin/env python3
"""
Simplified Laura-bot Flask Application for Testing
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'laura-bot-secret-key-2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Routes
@app.route('/')
def dashboard():
    return render_template('enhanced_dashboard.html')

@app.route('/learn')
def interactive_learning():
    return render_template('interactive_learning.html')

@app.route('/progress')
def progress():
    return render_template('progress_analytics.html')

@app.route('/hardware')
def hardware_control():
    return render_template('hardware_control.html')

@app.route('/quiz')
def quiz_interface():
    return render_template('quiz.html')

# API Routes
@app.route('/api/progress_data')
def progress_data():
    return jsonify({
        'success': True,
        'stats': {
            'sessions': 12,
            'study_time': 24.5,
            'avg_score': 87,
            'streak': 7
        }
    })

@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    subject = data.get('subject', 'general')
    difficulty = data.get('difficulty', 'medium')
    
    return jsonify({
        'success': True,
        'quiz_id': 'test_quiz_001',
        'subject': subject,
        'difficulty': difficulty,
        'message': f'Generated {difficulty} {subject} quiz successfully'
    })

@app.route('/api/hardware_control', methods=['POST'])
def hardware_control_api():
    data = request.get_json()
    action = data.get('action', '')
    
    return jsonify({
        'success': True,
        'action': action,
        'result': f'Hardware action "{action}" executed successfully (simulation)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/voice_interaction', methods=['POST'])
def voice_interaction_api():
    data = request.get_json()
    action = data.get('action', '')
    
    return jsonify({
        'success': True,
        'action': action,
        'result': f'Voice action "{action}" processed (simulation)',
        'timestamp': datetime.now().isoformat()
    })

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    print('🔌 Client connected')
    emit('status_update', {
        'message': 'Connected to Laura-bot!',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client disconnected')

if __name__ == '__main__':
    print("🚀 Starting Laura-bot Flask Application")
    print("🌐 Web Interface: http://localhost:5555")
    print("🤖 Hardware Status: Simulation Mode")
    print("📊 Learning System: Ready")
    print("=" * 50)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
    finally:
        print("🛑 Laura-bot server stopped")