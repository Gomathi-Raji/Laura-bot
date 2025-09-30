"""
Laura-bot Educational Flask Application - Working Version
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import os
import time
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'laura_bot_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
system_state = {
    'status': 'running',
    'hardware_connected': False,
    'learning_active': False,
    'current_subject': None
}

@app.route('/')
def index():
    return render_template('enhanced_dashboard.html')

@app.route('/learn')
def learn():
    return render_template('interactive_learning.html')

@app.route('/progress')
def progress():
    return render_template('progress_analytics.html')

@app.route('/api/progress_data')
def progress_data():
    # Simulate progress data
    stats = {
        'sessions': 12,
        'study_time': 24.5,
        'avg_score': 87,
        'streak': 7
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/simple')
def simple_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laura-bot Learning Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { 
                background: rgba(255,255,255,0.1); 
                backdrop-filter: blur(10px);
                border-radius: 15px; 
                padding: 25px; 
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            .card:hover { transform: translateY(-5px); }
            .card h2 { margin-bottom: 15px; color: #fff; }
            .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
            .status-item { 
                background: rgba(0,0,0,0.2); 
                padding: 10px; 
                border-radius: 8px; 
                text-align: center; 
            }
            .status-online { background: rgba(76, 175, 80, 0.3); }
            .status-offline { background: rgba(244, 67, 54, 0.3); }
            .btn { 
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 25px; 
                cursor: pointer; 
                margin: 5px; 
                font-size: 14px;
                transition: all 0.3s ease;
            }
            .btn:hover { 
                transform: scale(1.05); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .btn-secondary { background: linear-gradient(45deg, #2196F3, #1976D2); }
            .btn-warning { background: linear-gradient(45deg, #FF9800, #F57C00); }
            .response-area { 
                background: rgba(0,0,0,0.3); 
                padding: 15px; 
                border-radius: 10px; 
                margin-top: 15px; 
                min-height: 60px;
                display: none;
            }
            .subject-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .feature-list { list-style: none; }
            .feature-list li { 
                padding: 8px 0; 
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            .feature-list li:last-child { border-bottom: none; }
            .emoji { font-size: 1.2em; margin-right: 8px; }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Laura-bot</h1>
                <p>Advanced Learning Assistant with Arduino Integration</p>
            </div>
            
            <div class="dashboard">
                <!-- System Status Card -->
                <div class="card">
                    <h2>🔧 System Status</h2>
                    <div class="status-grid">
                        <div class="status-item status-online">
                            <div><span class="emoji">🌐</span>Web Server</div>
                            <small>Online</small>
                        </div>
                        <div class="status-item status-offline">
                            <div><span class="emoji">🤖</span>Arduino</div>
                            <small>Simulation</small>
                        </div>
                        <div class="status-item status-online">
                            <div><span class="emoji">🎓</span>Learning</div>
                            <small>Ready</small>
                        </div>
                        <div class="status-item status-online">
                            <div><span class="emoji">📊</span>Analytics</div>
                            <small>Active</small>
                        </div>
                    </div>
                    <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                </div>
                
                <!-- Learning Controls Card -->
                <div class="card">
                    <h2>🎓 Learning Center</h2>
                    <div style="margin-bottom: 15px;">
                        <button class="btn" onclick="startLearning()">📚 Start Learning</button>
                        <button class="btn btn-secondary" onclick="takeQuiz()">📝 Take Quiz</button>
                    </div>
                    <div class="subject-grid">
                        <button class="btn btn-warning" onclick="selectSubject('Math')">🔢 Math</button>
                        <button class="btn btn-warning" onclick="selectSubject('Science')">🧪 Science</button>
                        <button class="btn btn-warning" onclick="selectSubject('Physics')">⚛️ Physics</button>
                        <button class="btn btn-warning" onclick="selectSubject('Chemistry')">🧬 Chemistry</button>
                    </div>
                    <div class="response-area" id="learning-response"></div>
                </div>
                
                <!-- Hardware Controls Card -->
                <div class="card">
                    <h2>🤖 Hardware Control</h2>
                    <div style="margin-bottom: 15px;">
                        <button class="btn" onclick="testHardware()">🔧 Test Hardware</button>
                        <button class="btn btn-secondary" onclick="testVoice()">🎤 Test Voice</button>
                    </div>
                    <div>
                        <button class="btn btn-warning" onclick="gestureControl()">👋 Gesture Control</button>
                        <button class="btn btn-warning" onclick="servoTest()">⚙️ Servo Test</button>
                    </div>
                    <div class="response-area" id="hardware-response"></div>
                </div>
                
                <!-- Features Overview Card -->
                <div class="card">
                    <h2>✨ Available Features</h2>
                    <ul class="feature-list">
                        <li><span class="emoji">🎯</span>Interactive Learning Sessions</li>
                        <li><span class="emoji">📝</span>Adaptive Quiz Generation</li>
                        <li><span class="emoji">🎤</span>Voice Recognition & Synthesis</li>
                        <li><span class="emoji">👋</span>Gesture-Based Navigation</li>
                        <li><span class="emoji">📊</span>Progress Tracking & Analytics</li>
                        <li><span class="emoji">🤖</span>Arduino Hardware Integration</li>
                        <li><span class="emoji">🎨</span>Multi-Subject Content</li>
                        <li><span class="emoji">⚡</span>Real-Time Feedback</li>
                    </ul>
                </div>
                
                <!-- Progress Tracking Card -->
                <div class="card">
                    <h2>📊 Progress & Analytics</h2>
                    <div style="margin-bottom: 15px;">
                        <button class="btn" onclick="viewProgress()">📈 View Progress</button>
                        <button class="btn btn-secondary" onclick="viewAnalytics()">📊 Analytics</button>
                    </div>
                    <div>
                        <button class="btn btn-warning" onclick="exportData()">💾 Export Data</button>
                        <button class="btn btn-warning" onclick="resetProgress()">🔄 Reset</button>
                    </div>
                    <div class="response-area" id="progress-response"></div>
                </div>
                
                <!-- System Information Card -->
                <div class="card">
                    <h2>ℹ️ System Information</h2>
                    <div class="feature-list" style="font-size: 0.9em;">
                        <li><strong>Version:</strong> Laura-bot v2.0</li>
                        <li><strong>Platform:</strong> Flask + SocketIO</li>
                        <li><strong>Port:</strong> 5555</li>
                        <li><strong>Mode:</strong> Development</li>
                        <li><strong>Database:</strong> SQLite</li>
                        <li><strong>Hardware:</strong> Simulation Mode</li>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Initialize Socket.IO connection
            const socket = io();
            
            // Socket event handlers
            socket.on('connect', function() {
                console.log('Connected to Laura-bot server');
                updateConnectionStatus(true);
            });
            
            socket.on('disconnect', function() {
                console.log('Disconnected from server');
                updateConnectionStatus(false);
            });
            
            socket.on('status_update', function(data) {
                console.log('Status update received:', data);
            });
            
            // UI Functions
            function showResponse(elementId, message, type = 'info') {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div style="color: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#74c0fc'};">${message}</div>`;
                element.style.display = 'block';
                setTimeout(() => element.style.display = 'none', 5000);
            }
            
            function updateConnectionStatus(connected) {
                // Update status indicators
                console.log('Connection status:', connected);
            }
            
            // Learning Functions
            function startLearning() {
                showResponse('learning-response', '🎓 Learning session initialized!<br>Ready to begin your educational journey.', 'success');
                fetch('/api/start_session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })
                    .then(response => response.json())
                    .then(data => console.log('Session started:', data));
            }
            
            function takeQuiz() {
                showResponse('learning-response', '📝 Quiz system activated!<br>Select a subject to begin assessment.', 'info');
            }
            
            function selectSubject(subject) {
                showResponse('learning-response', `📚 Subject selected: ${subject}<br>Loading curriculum and interactive content...`, 'info');
            }
            
            // Hardware Functions
            function testHardware() {
                showResponse('hardware-response', '🤖 Hardware testing initiated!<br>Arduino controller responding in simulation mode.', 'success');
            }
            
            function testVoice() {
                showResponse('hardware-response', '🎤 Voice system test initiated!<br>Speech recognition and synthesis ready.', 'success');
            }
            
            function gestureControl() {
                showResponse('hardware-response', '👋 Gesture recognition activated!<br>Camera system monitoring hand movements.', 'info');
            }
            
            function servoTest() {
                showResponse('hardware-response', '⚙️ Servo test sequence initiated!<br>Testing all motor positions and animations.', 'info');
            }
            
            // Progress Functions
            function viewProgress() {
                showResponse('progress-response', '📈 Loading progress analytics...<br>Displaying learning achievements and milestones.', 'info');
            }
            
            function viewAnalytics() {
                showResponse('progress-response', '📊 Analytics dashboard loading...<br>Comprehensive learning statistics available.', 'info');
            }
            
            function exportData() {
                showResponse('progress-response', '💾 Exporting learning data...<br>Progress reports and analytics being generated.', 'success');
            }
            
            function resetProgress() {
                if(confirm('Are you sure you want to reset all progress data?')) {
                    showResponse('progress-response', '🔄 Progress data reset initiated...<br>All learning statistics cleared.', 'success');
                }
            }
            
            // System Functions
            function refreshStatus() {
                showResponse('learning-response', '🔄 Refreshing system status...<br>Checking all components and connections.', 'info');
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => console.log('System status:', data));
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    return jsonify({
        'success': True,
        'status': 'running',
        'system': 'Laura-bot Learning Assistant',
        'hardware_connected': system_state['hardware_connected'],
        'learning_active': system_state['learning_active'],
        'features': {
            'web_interface': True,
            'learning_modules': True,
            'arduino_integration': True,
            'voice_interaction': True,
            'progress_tracking': True,
            'gesture_control': True
        }
    })

@app.route('/api/start_session', methods=['POST'])
def start_session():
    system_state['learning_active'] = True
    session_id = f"session_{int(time.time())}"
    system_state['current_session'] = session_id
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Learning session started successfully!'
    })

@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    subject = data.get('subject', 'General')
    difficulty = data.get('difficulty', 1)
    num_questions = data.get('num_questions', 5)
    
    # Simulate quiz generation
    quiz = {
        'subject': subject,
        'difficulty': difficulty,
        'questions': [
            {
                'question': f'Question {i+1} for {subject}',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct': 'A'
            } for i in range(num_questions)
        ]
    }
    
    return jsonify({
        'success': True,
        'quiz': quiz,
        'message': f'Quiz generated for {subject}'
    })

@app.route('/api/hardware_control', methods=['POST'])
def api_hardware_control():
    data = request.get_json()
    action = data.get('action', '')
    
    # Simulate hardware responses
    responses = {
        'test_servo': 'Servo motors tested successfully',
        'voice': 'Voice synthesis test completed',
        'gesture': 'Gesture recognition toggled',
        'speak': 'Status announcement played'
    }
    
    result = responses.get(action, f'Unknown action: {action}')
    
    return jsonify({
        'success': True,
        'result': result,
        'message': f'Hardware action "{action}" completed'
    })

@app.route('/api/voice_interaction', methods=['POST'])
def voice_interaction():
    data = request.get_json()
    action = data.get('action', '')
    
    if action == 'start_listening':
        return jsonify({
            'success': True,
            'message': 'Voice listening started (simulation mode)'
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid voice action'
    })

@app.route('/hardware')
def hardware_control():
    return render_template('hardware_control.html')

@app.route('/quiz')
def quiz_interface():
    return render_template('quiz.html')

@socketio.on('connect')
def handle_connect():
    print('🔌 Client connected')
    emit('status_update', system_state)
    emit('welcome_message', {
        'message': 'Welcome to Laura-bot Learning System!',
        'timestamp': datetime.now().isoformat(),
        'features': ['Voice Control', 'Interactive Learning', 'Real-time Progress', 'Hardware Integration']
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client disconnected')

@socketio.on('join_learning_session')
def handle_join_learning_session(data):
    """Handle user joining a learning session"""
    user_id = data.get('user_id', 'anonymous')
    subject = data.get('subject', 'general')
    
    print(f'👨‍🎓 User {user_id} joined {subject} learning session')
    
    emit('learning_session_joined', {
        'success': True,
        'subject': subject,
        'session_id': f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'message': f'Joined {subject} learning session successfully',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('progress_update')
def handle_progress_update(data):
    """Handle real-time progress updates"""
    progress_data = {
        'user_id': data.get('user_id', 'anonymous'),
        'subject': data.get('subject', 'general'),
        'score': data.get('score', 0),
        'time_spent': data.get('time_spent', 0),
        'questions_answered': data.get('questions_answered', 0),
        'timestamp': datetime.now().isoformat()
    }
    
    # Broadcast progress update to all connected clients
    emit('live_progress_update', progress_data, broadcast=True)
    
    print(f'📊 Progress update: {progress_data["subject"]} - Score: {progress_data["score"]}%')

@socketio.on('hardware_status_request')
def handle_hardware_status_request():
    """Handle hardware status requests"""
    hardware_status = {
        'arduino': {
            'connected': True,
            'mode': 'simulation',
            'temperature': 25.3,
            'voltage': 5.0,
            'uptime': '02:15:33'
        },
        'servo_motors': {
            'servo1': {'position': 90, 'status': 'active'},
            'servo2': {'position': 45, 'status': 'active'}
        },
        'voice_system': {
            'status': 'ready',
            'recognition_active': False,
            'synthesis_ready': True
        },
        'gesture_recognition': {
            'camera_active': False,
            'last_gesture': 'none',
            'confidence': 0
        },
        'timestamp': datetime.now().isoformat()
    }
    
    emit('hardware_status_update', hardware_status)

@socketio.on('voice_command')
def handle_voice_command(data):
    """Handle voice commands from clients"""
    command = data.get('command', '').lower()
    confidence = data.get('confidence', 0)
    
    response = {
        'command': command,
        'confidence': confidence,
        'processed': True,
        'timestamp': datetime.now().isoformat()
    }
    
    # Process different voice commands
    if 'start quiz' in command:
        response['action'] = 'quiz_started'
        response['message'] = 'Starting quiz session...'
    elif 'next question' in command:
        response['action'] = 'next_question'
        response['message'] = 'Moving to next question...'
    elif 'repeat question' in command:
        response['action'] = 'repeat_question'
        response['message'] = 'Repeating current question...'
    elif 'help' in command:
        response['action'] = 'show_help'
        response['message'] = 'Showing available commands...'
    else:
        response['action'] = 'unknown_command'
        response['message'] = f'Command "{command}" not recognized'
    
    emit('voice_command_response', response)
    
    # Broadcast voice activity to other clients
    emit('voice_activity', {
        'user': 'student',
        'command': command,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True, include_self=False)

@socketio.on('gesture_detected')
def handle_gesture_detected(data):
    """Handle gesture detection events"""
    gesture = data.get('gesture', 'none')
    confidence = data.get('confidence', 0)
    
    gesture_response = {
        'gesture': gesture,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    }
    
    # Process different gestures
    if gesture == 'thumbs_up':
        gesture_response['action'] = 'positive_feedback'
        gesture_response['message'] = 'Great job! Keep it up!'
    elif gesture == 'peace':
        gesture_response['action'] = 'pause_session'
        gesture_response['message'] = 'Pausing current session...'
    elif gesture == 'fist':
        gesture_response['action'] = 'stop_session'
        gesture_response['message'] = 'Stopping current session...'
    elif gesture == 'open_palm':
        gesture_response['action'] = 'help_request'
        gesture_response['message'] = 'How can I help you?'
    else:
        gesture_response['action'] = 'gesture_acknowledged'
        gesture_response['message'] = f'Gesture "{gesture}" detected'
    
    emit('gesture_response', gesture_response)
    
    # Broadcast gesture activity
    emit('gesture_activity', gesture_response, broadcast=True, include_self=False)

@socketio.on('quiz_interaction')
def handle_quiz_interaction(data):
    """Handle quiz-related interactions"""
    action = data.get('action', '')
    quiz_data = data.get('data', {})
    
    if action == 'answer_submitted':
        # Process quiz answer
        answer = quiz_data.get('answer', '')
        question_id = quiz_data.get('question_id', '')
        
        # Simulate answer checking
        is_correct = True  # This would normally check against correct answer
        
        response = {
            'question_id': question_id,
            'answer': answer,
            'correct': is_correct,
            'explanation': 'This is the correct answer because...',
            'score_change': 10 if is_correct else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        emit('quiz_answer_result', response)
        
    elif action == 'hint_requested':
        hint_response = {
            'question_id': quiz_data.get('question_id', ''),
            'hint': 'Think about the fundamental principles involved...',
            'hint_level': quiz_data.get('hint_level', 1),
            'timestamp': datetime.now().isoformat()
        }
        
        emit('quiz_hint_provided', hint_response)

@socketio.on('learning_analytics_request')
def handle_learning_analytics_request(data):
    """Handle requests for learning analytics data"""
    time_period = data.get('period', 'week')  # week, month, year
    subject = data.get('subject', 'all')
    
    # Generate mock analytics data
    analytics_data = {
        'period': time_period,
        'subject': subject,
        'total_sessions': 24,
        'average_score': 87.5,
        'time_spent_hours': 15.5,
        'improvement_rate': 12.3,
        'strong_topics': ['Algebra', 'Chemistry Basics', 'Grammar'],
        'areas_for_improvement': ['Geometry', 'Physics Concepts', 'Essay Writing'],
        'daily_progress': [85, 78, 92, 88, 95, 90, 87],
        'subject_breakdown': {
            'Math': 35,
            'Science': 30,
            'English': 20,
            'History': 15
        },
        'achievements': [
            {'name': 'Math Master', 'earned_date': '2024-01-15', 'type': 'subject'},
            {'name': 'Streak Keeper', 'earned_date': '2024-01-10', 'type': 'consistency'}
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    emit('learning_analytics_data', analytics_data)

@socketio.on('system_monitoring_request')
def handle_system_monitoring_request():
    """Handle system monitoring requests"""
    import random
    
    system_metrics = {
        'cpu_usage': random.randint(30, 70),
        'memory_usage': random.randint(50, 80),
        'disk_usage': random.randint(20, 60),
        'network_status': 'good',
        'active_sessions': random.randint(1, 5),
        'database_health': 'excellent',
        'response_time': round(random.uniform(50, 200), 2),
        'uptime': '5 days, 12 hours',
        'timestamp': datetime.now().isoformat()
    }
    
    emit('system_metrics_update', system_metrics)

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