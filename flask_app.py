"""
Laura-bot Advanced Learning Assistant with Arduino Integration
Flask Web Application combining hardware control with educational features
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Laura-bot modules with graceful error handling
HARDWARE_AVAILABLE = False
LEARNING_MODULES_AVAILABLE = False
AI_AVAILABLE = False
VOICE_AVAILABLE = False

# Voice modules
try:
    from voice.speaker import speak, board
    from voice.listener import listen
    VOICE_AVAILABLE = True
    HARDWARE_AVAILABLE = board is not None
    print("✅ Voice modules loaded successfully")
except Exception as e:
    print(f"⚠️ Voice modules unavailable: {e}")
    # Create fallback functions
    def speak(text):
        print(f"🤖 Laura-bot: {text}")
    def listen():
        return ""

# AI modules
try:
    from ai.gemini_ai import get_response, get_tutor_response, generate_quiz, generate_explanation
    AI_AVAILABLE = True
    print("✅ AI modules loaded successfully")
except Exception as e:
    print(f"⚠️ AI modules unavailable: {e}")
    # Create fallback functions
    def get_response(text):
        return "AI response unavailable. Please check AI configuration."
    def get_tutor_response(text, subject=None):
        return "AI tutor unavailable. Please check AI configuration."
    def generate_quiz(subject, difficulty="medium"):
        return {"question": "Quiz unavailable", "options": ["A", "B", "C", "D"], "correct": 0}
    def generate_explanation(topic):
        return "Explanation unavailable. Please check AI configuration."

# Learning modules
try:
    from learning_tracker import LearningTracker, start_session, end_session
    from education_modules import get_education_module, list_available_subjects
    LEARNING_MODULES_AVAILABLE = True
    print("✅ Learning modules loaded successfully")
except Exception as e:
    print(f"⚠️ Learning modules unavailable: {e}")
    # Create fallback functions
    def start_session(user_id="default"):
        return {"session_id": "fallback"}
    def end_session(session_id):
        return {"status": "ended"}
    def list_available_subjects():
        return ["Mathematics", "Science", "Literature", "History"]
    def get_education_module(subject):
        return None

# Arduino controller
try:
    from arduino.educational_controller import ArduinoEducationalController
    print("✅ Arduino controller module loaded successfully")
except Exception as e:
    print(f"⚠️ Arduino controller unavailable: {e}")
    # Create fallback class
    class ArduinoEducationalController:
        def __init__(self):
            self.connected = False
        def move_servo(self, angle):
            print(f"Servo simulation: {angle} degrees")
        def control_led(self, state):
            print(f"LED simulation: {'ON' if state else 'OFF'}")
        def read_sensor(self):
            return 50  # Simulated sensor value

# Initialize Flask app with SocketIO for real-time communication
app = Flask(__name__)
app.config['SECRET_KEY'] = 'laura_bot_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize learning tracker
try:
    learning_tracker = LearningTracker()
    print("📊 Learning tracker initialized")
except Exception as e:
    print(f"⚠️ Learning tracker error: {e}")
    learning_tracker = None

# Initialize Arduino controller
try:
    arduino_controller = ArduinoEducationalController()
    print("🤖 Arduino controller initialized")
except Exception as e:
    print(f"⚠️ Arduino controller error: {e}")
    arduino_controller = None

# Global state
current_session = {
    'user_name': 'Student',
    'session_id': None,
    'learning_mode': 'standby',
    'current_subject': None,
    'quiz_in_progress': False,
    'quiz_data': None,
    'question_index': 0,
    'score': 0,
    'listening': False,
    'hardware_status': 'connected' if HARDWARE_AVAILABLE else 'simulation'
}

# Database initialization
def init_database():
    """Initialize SQLite database for learning data"""
    conn = sqlite3.connect('learning_data/laura_learning.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_name TEXT,
            interaction_type TEXT,
            subject TEXT,
            topic TEXT,
            content TEXT,
            response TEXT,
            hardware_used BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_name TEXT,
            subject TEXT,
            topic TEXT,
            questions_total INTEGER,
            questions_correct INTEGER,
            score_percentage REAL,
            difficulty_level INTEGER,
            time_taken INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("📊 Database initialized successfully")

# Initialize database on startup
init_database()

# Route: Main Dashboard
@app.route('/')
def dashboard():
    """Main learning dashboard with mobile detection"""
    # Check if user is on mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    # Use mobile template for mobile devices
    template = 'mobile_dashboard.html' if is_mobile else 'dashboard.html'
    
    return render_template(template, 
                         hardware_status=current_session['hardware_status'],
                         available_subjects=list_available_subjects() if LEARNING_MODULES_AVAILABLE else [],
                         session=current_session)

# Route: Learning Interface
@app.route('/learn')
def learning_interface():
    """Interactive learning interface with mobile detection"""
    # Check if user is on mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    # Use mobile template for mobile devices
    template = 'mobile_learn.html' if is_mobile else 'learn.html'
    
    return render_template(template,
                         session=current_session,
                         available_subjects=list_available_subjects() if LEARNING_MODULES_AVAILABLE else [])

# Route: Progress Analytics
@app.route('/progress')
def progress_analytics():
    """Learning progress and analytics"""
    if learning_tracker:
        stats = learning_tracker.get_user_stats(current_session['user_name'])
        recent_sessions = learning_tracker.get_recent_sessions(current_session['user_name'], 10)
        return render_template('progress.html', stats=stats, sessions=recent_sessions)
    else:
        return render_template('progress.html', stats={}, sessions=[])

# Route: Hardware Control
@app.route('/hardware')
def hardware_control():
    """Arduino hardware control interface"""
    return render_template('hardware.html', 
                         hardware_available=HARDWARE_AVAILABLE,
                         hardware_status=current_session['hardware_status'])

# API Route: Start Learning Session
@app.route('/api/start_session', methods=['POST'])
def start_learning_session():
    """Start a new learning session"""
    data = request.get_json()
    user_name = data.get('user_name', 'Student')
    subject = data.get('subject', 'General')
    
    current_session['user_name'] = user_name
    current_session['current_subject'] = subject
    current_session['learning_mode'] = 'active'
    
    # Start tracking session
    if learning_tracker:
        session_id = start_session(user_name, subject)
        current_session['session_id'] = session_id
    
    # Hardware acknowledgment
    if HARDWARE_AVAILABLE:
        threading.Thread(target=lambda: speak(f"வணக்கம் {user_name}! {subject} கற்கத் தொடங்குவோம்!")).start()
    
    # Log interaction
    log_interaction('session_start', subject, 'Session Started', f"Learning session started for {subject}")
    
    return jsonify({
        'success': True,
        'session_id': current_session['session_id'],
        'message': f'Learning session started for {subject}'
    })

# API Route: Generate Quiz
@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz_api():
    """Generate quiz questions for a subject"""
    data = request.get_json()
    subject = data.get('subject', 'Math')
    topic = data.get('topic', 'General')
    difficulty = data.get('difficulty', 1)
    num_questions = data.get('num_questions', 5)
    
    try:
        # Try structured education modules first
        if LEARNING_MODULES_AVAILABLE:
            education_module = get_education_module(subject)
            if education_module and hasattr(education_module, 'generate_quiz_questions'):
                quiz_questions = education_module.generate_quiz_questions(topic, difficulty, num_questions)
                if quiz_questions and not any('error' in q for q in quiz_questions):
                    quiz_data = {
                        'subject': subject,
                        'topic': topic,
                        'difficulty': difficulty,
                        'questions': quiz_questions,
                        'total_questions': len(quiz_questions),
                        'source': 'structured_module'
                    }
                else:
                    raise Exception("Structured module failed")
            else:
                raise Exception("No structured module available")
        else:
            raise Exception("Learning modules not available")
            
    except Exception as e:
        print(f"⚠️ Structured quiz generation failed: {e}")
        # Fallback to AI generation
        try:
            quiz_data = generate_quiz(subject, topic, difficulty, num_questions)
            quiz_data['source'] = 'ai_generated'
        except Exception as ai_error:
            print(f"⚠️ AI quiz generation failed: {ai_error}")
            # Create simple fallback quiz
            quiz_data = {
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty,
                'questions': [{
                    'question': f"What is an important concept in {subject}?",
                    'options': ['A) Basic understanding', 'B) Advanced theory', 'C) Practical application', 'D) All of the above'],
                    'correct_answer': 'D',
                    'explanation': f'{subject} involves understanding, theory, and practical application.'
                }],
                'total_questions': 1,
                'source': 'fallback'
            }
    
    # Store quiz data
    current_session['quiz_data'] = quiz_data
    current_session['quiz_in_progress'] = True
    current_session['question_index'] = 0
    current_session['score'] = 0
    
    # Hardware acknowledgment
    if HARDWARE_AVAILABLE:
        threading.Thread(target=lambda: speak(f"{subject} வினாடி வினாக்கள் தயார்! கேட்க தொடங்குகிறோம்!")).start()
    
    # Log interaction
    log_interaction('quiz_start', subject, topic, f"Quiz generated with {len(quiz_data['questions'])} questions")
    
    return jsonify({
        'success': True,
        'quiz_data': quiz_data,
        'current_question': quiz_data['questions'][0] if quiz_data['questions'] else None
    })

# API Route: Submit Quiz Answer
@app.route('/api/submit_answer', methods=['POST'])
def submit_quiz_answer():
    """Submit answer for current quiz question"""
    data = request.get_json()
    answer = data.get('answer', '').upper()
    
    if not current_session['quiz_in_progress'] or not current_session['quiz_data']:
        return jsonify({'success': False, 'error': 'No active quiz'})
    
    quiz_data = current_session['quiz_data']
    current_question = quiz_data['questions'][current_session['question_index']]
    correct_answer = current_question['correct_answer']
    
    is_correct = answer == correct_answer
    if is_correct:
        current_session['score'] += 1
    
    # Hardware feedback
    if HARDWARE_AVAILABLE:
        feedback_text = "சரியான பதில்!" if is_correct else "தவறான பதில். மீண்டும் முயற்சி செய்!"
        threading.Thread(target=lambda: speak(feedback_text)).start()
    
    # Move to next question
    current_session['question_index'] += 1
    
    # Check if quiz is complete
    quiz_complete = current_session['question_index'] >= len(quiz_data['questions'])
    next_question = None
    
    if not quiz_complete:
        next_question = quiz_data['questions'][current_session['question_index']]
    else:
        # Quiz completed - save results
        if learning_tracker:
            learning_tracker.record_quiz(
                current_session['user_name'],
                quiz_data['subject'],
                quiz_data['topic'],
                len(quiz_data['questions']),
                current_session['score'],
                quiz_data['difficulty']
            )
        
        current_session['quiz_in_progress'] = False
        
        # Hardware completion message
        if HARDWARE_AVAILABLE:
            score_percentage = (current_session['score'] / len(quiz_data['questions'])) * 100
            completion_text = f"வினாடி வினா முடிந்தது! உங்கள் மதிப்பெண்: {score_percentage:.1f}%"
            threading.Thread(target=lambda: speak(completion_text)).start()
    
    # Log interaction
    log_interaction('quiz_answer', quiz_data['subject'], quiz_data['topic'], 
                   f"Answer: {answer}, Correct: {is_correct}")
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': current_question.get('explanation', ''),
        'score': current_session['score'],
        'quiz_complete': quiz_complete,
        'next_question': next_question,
        'final_score_percentage': (current_session['score'] / len(quiz_data['questions'])) * 100 if quiz_complete else None
    })

# API Route: Get Explanation
@app.route('/api/get_explanation', methods=['POST'])
def get_explanation_api():
    """Get explanation for a topic"""
    data = request.get_json()
    subject = data.get('subject', 'General')
    topic = data.get('topic', 'General')
    level = data.get('level', 'beginner')
    
    try:
        explanation = generate_explanation(topic, subject, level)
        
        # Hardware speech
        if HARDWARE_AVAILABLE:
            # Speak a summary in Tamil
            threading.Thread(target=lambda: speak(f"{topic} பற்றி விளக்கம் கொடுக்கிறேன்")).start()
        
        # Log interaction
        log_interaction('explanation', subject, topic, explanation[:200] + "...")
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'subject': subject,
            'topic': topic
        })
        
    except Exception as e:
        print(f"⚠️ Explanation generation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate explanation',
            'fallback': f"I'd like to explain {topic} in {subject}, but I'm having technical difficulties right now."
        })

# API Route: Voice Interaction
@app.route('/api/voice_interaction', methods=['POST'])
def voice_interaction():
    """Handle voice input and provide voice response"""
    data = request.get_json()
    action = data.get('action', 'listen')
    
    if action == 'start_listening':
        current_session['listening'] = True
        
        def listen_and_respond():
            try:
                # Listen for voice input
                user_input = listen()  # This should return the recognized speech
                
                if user_input:
                    # Process with AI
                    if current_session['learning_mode'] == 'active':
                        response = get_tutor_response(user_input, current_session.get('current_subject', ''))
                    else:
                        response = get_response(user_input)
                    
                    # Speak response
                    if HARDWARE_AVAILABLE:
                        speak(response)
                    
                    # Log interaction
                    log_interaction('voice', current_session.get('current_subject', 'General'), 
                                  'Voice Input', f"User: {user_input} | Response: {response[:100]}...")
                    
                    # Emit to frontend via SocketIO
                    socketio.emit('voice_response', {
                        'user_input': user_input,
                        'ai_response': response,
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"⚠️ Voice interaction error: {e}")
                socketio.emit('voice_error', {'error': str(e)})
            finally:
                current_session['listening'] = False
        
        # Start listening in background thread
        threading.Thread(target=listen_and_respond).start()
        
        return jsonify({'success': True, 'status': 'listening_started'})
    
    elif action == 'stop_listening':
        current_session['listening'] = False
        return jsonify({'success': True, 'status': 'listening_stopped'})

# API Route: Hardware Control
@app.route('/api/hardware_control', methods=['POST'])
def hardware_control_api():
    """Control Arduino hardware"""
    data = request.get_json()
    action = data.get('action', '')
    
    if not HARDWARE_AVAILABLE:
        return jsonify({'success': False, 'error': 'Hardware not available'})
    
    try:
        if action == 'test_servos':
            # Test servo movement
            def test_servos():
                for angle in [0, 90, 180, 90, 0]:
                    if board:
                        board.digital[9].write(angle)
                        board.digital[10].write(angle)
                        time.sleep(0.5)
            
            threading.Thread(target=test_servos).start()
            return jsonify({'success': True, 'message': 'Servo test started'})
            
        elif action == 'speak_text':
            text = data.get('text', 'வணக்கம்!')
            threading.Thread(target=lambda: speak(text)).start()
            return jsonify({'success': True, 'message': 'Speech started'})
            
        elif action == 'celebration':
            # Celebration animation with sound
            def celebrate():
                speak("வாழ்த்துக்கள்! நன்றாக படித்தீர்கள்!")
                for i in range(3):
                    if board:
                        board.digital[9].write(180)
                        board.digital[10].write(0)
                        time.sleep(0.3)
                        board.digital[9].write(0)
                        board.digital[10].write(180)
                        time.sleep(0.3)
            
            threading.Thread(target=celebrate).start()
            return jsonify({'success': True, 'message': 'Celebration started'})
        
        else:
            return jsonify({'success': False, 'error': 'Unknown action'})
            
    except Exception as e:
        print(f"⚠️ Hardware control error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# API Route: Get System Status
@app.route('/api/status')
def get_system_status():
    """Get current system status"""
    return jsonify({
        'session': current_session,
        'hardware_available': HARDWARE_AVAILABLE,
        'learning_modules_available': LEARNING_MODULES_AVAILABLE,
        'available_subjects': list_available_subjects() if LEARNING_MODULES_AVAILABLE else [],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/subjects')
def get_subjects():
    """Get available subjects"""
    return jsonify({
        'subjects': list_available_subjects() if LEARNING_MODULES_AVAILABLE else ['Mathematics', 'Science', 'Literature', 'History'],
        'success': True
    })

@app.route('/api/progress/summary')
def get_progress_summary():
    """Get learning progress summary"""
    try:
        if learning_tracker:
            # Get real progress data
            progress_data = learning_tracker.get_progress_summary()
        else:
            # Return sample data
            progress_data = {
                'sessions': 12,
                'studyTime': '5h 30m',
                'achievements': 8,
                'mathProgress': 75,
                'scienceProgress': 60,
                'overallProgress': 68
            }
        
        return jsonify({
            'success': True,
            **progress_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'sessions': 0,
            'studyTime': '0h 0m',
            'achievements': 0,
            'mathProgress': 0,
            'scienceProgress': 0,
            'overallProgress': 0
        })

@app.route('/api/hardware/status')
def get_hardware_status():
    """Get hardware connection status"""
    try:
        if arduino_controller:
            connected = arduino_controller.connected if hasattr(arduino_controller, 'connected') else HARDWARE_AVAILABLE
        else:
            connected = False
            
        return jsonify({
            'connected': connected,
            'available': HARDWARE_AVAILABLE,
            'mode': 'real' if connected else 'simulation',
            'success': True
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'available': False,
            'mode': 'simulation',
            'success': False,
            'error': str(e)
        })

# Utility function: Log interactions
def log_interaction(interaction_type, subject, topic, content, response=''):
    """Log interaction to database"""
    try:
        conn = sqlite3.connect('learning_data/laura_learning.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions 
            (user_name, interaction_type, subject, topic, content, response, hardware_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_session['user_name'],
            interaction_type,
            subject,
            topic,
            content,
            response,
            HARDWARE_AVAILABLE
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Logging error: {e}")

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"🔗 Client connected")
    emit('status_update', get_system_status()['data'] if hasattr(get_system_status(), 'data') else {})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"🔌 Client disconnected")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('status_update', {
        'session': current_session,
        'hardware_available': HARDWARE_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🚀 Starting Laura-bot Advanced Learning Assistant...")
    print(f"🔧 Hardware Status: {'Connected' if HARDWARE_AVAILABLE else 'Simulation Mode'}")
    print(f"🎓 Learning Modules: {'Available' if LEARNING_MODULES_AVAILABLE else 'Limited'}")
    print(f"🌐 Web Interface: http://localhost:5555")
    
    # Run Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
