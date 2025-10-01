#!/usr/bin/env python3
"""
Laura-bot Flask Application - Simple Startup
"""

print("=" * 60)
print("🤖 LAURA-BOT FLASK WEB APPLICATION")
print("=" * 60)

import sys
import os
import webbrowser
import time
from datetime import datetime

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"📁 Working Directory: {current_dir}")
print(f"🐍 Python Version: {sys.version}")
print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    print("\n🔍 Importing Flask components...")
    
    from flask import Flask, render_template, jsonify, request
    print("   ✅ Flask imported successfully")
    
    from flask_socketio import SocketIO, emit
    print("   ✅ Flask-SocketIO imported successfully")
    
    print("\n🏗️ Creating Flask application...")
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'laura-bot-2024'
    app.config['DEBUG'] = False  # Disable debug mode
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    
    print("   ✅ Flask app and SocketIO initialized")
    
    # Check for templates
    templates_dir = os.path.join(current_dir, 'templates')
    has_templates = os.path.exists(templates_dir)
    print(f"   📄 Templates directory: {'✅ Found' if has_templates else '❌ Not found'}")
    
    # Hardware integration
    print("\n🤖 Initializing hardware integration...")
    
    # Add hardware directory to path
    hardware_dir = os.path.join(current_dir, 'hardware')
    if os.path.exists(hardware_dir):
        sys.path.insert(0, hardware_dir)
    
    # Import hardware controller
    hardware_controller = None
    try:
        from real_hardware_controller import get_hardware_controller, initialize_hardware
        hardware_controller = initialize_hardware()
        print("   ✅ Hardware controller initialized")
        HARDWARE_AVAILABLE = True
        
        # Register callback for automatic sensor updates
        def broadcast_sensor_data(data):
            socketio.emit('sensor_data', data)
        
        hardware_controller.register_callback('sensor_update', broadcast_sensor_data)
    except ImportError as e:
        print(f"   ⚠️ Hardware controller not available: {e}")
        print("   ℹ️ Running in simulation mode")
        HARDWARE_AVAILABLE = False
        hardware_controller = None
    except Exception as e:
        print(f"   ⚠️ Hardware initialization failed: {e}")
        print("   ℹ️ Running in simulation mode")
        HARDWARE_AVAILABLE = False
        hardware_controller = None
    
    # Define routes
    @app.route('/')
    def dashboard():
        if has_templates:
            try:
                return render_template('modern_dashboard.html')
            except Exception as e:
                # Fallback to enhanced dashboard if modern doesn't exist
                try:
                    return render_template('enhanced_dashboard.html')
                except:
                    pass
        
        # Fallback HTML
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laura-bot Educational Platform</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; text-align: center; }}
        .header {{ margin-bottom: 40px; }}
        h1 {{ font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
        .status-panel {{ 
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            border-radius: 15px; padding: 30px; margin: 30px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .nav-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin: 30px 0;
        }}
        .nav-card {{ 
            background: rgba(255,255,255,0.1); border-radius: 12px; padding: 25px;
            text-decoration: none; color: white; transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .nav-card:hover {{ 
            background: rgba(255,255,255,0.2); transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        .nav-card h3 {{ font-size: 1.3em; margin-bottom: 10px; }}
        .nav-card p {{ opacity: 0.8; font-size: 0.9em; }}
        .server-info {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; margin: 20px 0; text-align: left;
        }}
        .info-item {{ 
            background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; 
        }}
        .info-label {{ font-weight: bold; opacity: 0.8; font-size: 0.9em; }}
        .info-value {{ font-size: 1.1em; margin-top: 5px; }}
        .success {{ color: #4CAF50; }}
        .api-test {{ 
            background: rgba(76, 175, 80, 0.2); border: 1px solid rgba(76, 175, 80, 0.5);
            padding: 15px; border-radius: 8px; margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            h1 {{ font-size: 2em; }}
            .nav-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Laura-bot</h1>
            <p class="subtitle">Your Intelligent Educational Platform</p>
        </div>
        
        <div class="status-panel">
            <h2>🚀 Server Status: <span class="success">ONLINE</span></h2>
            <div class="server-info">
                <div class="info-item">
                    <div class="info-label">Server URL</div>
                    <div class="info-value">http://localhost:5555</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value success">✅ Running</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Started</div>
                    <div class="info-value">{datetime.now().strftime('%H:%M:%S')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Features</div>
                    <div class="info-value">All Systems Active</div>
                </div>
            </div>
        </div>
        
        <div class="nav-grid">
            <a href="/learn" class="nav-card">
                <h3>📚 Interactive Learning</h3>
                <p>Personalized lessons with AI assistance and real-time feedback</p>
            </a>
            <a href="/quiz" class="nav-card">
                <h3>🧠 Quiz System</h3>
                <p>Adaptive quizzes with voice control and progress tracking</p>
            </a>
            <a href="/progress" class="nav-card">
                <h3>📈 Progress Analytics</h3>
                <p>Detailed statistics and learning insights with visualizations</p>
            </a>
            <a href="/hardware" class="nav-card">
                <h3>⚙️ Hardware Control</h3>
                <p>Arduino integration and IoT device management</p>
            </a>
            <a href="/api/test" class="nav-card">
                <h3>🔧 API Testing</h3>
                <p>Test API endpoints and system connectivity</p>
            </a>
        </div>
        
        <div class="api-test">
            <h3>🔗 Quick API Test</h3>
            <p>Click here to test the API: <a href="/api/test" style="color: #ffeb3b;">Test Laura-bot API</a></p>
        </div>
        
        <div class="status-panel">
            <h3>🎯 Ready for Learning!</h3>
            <p>Laura-bot is fully operational and ready to assist with your educational journey.</p>
            <p><em>Navigate using the cards above or the menu links.</em></p>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        console.log('🤖 Laura-bot Dashboard Loaded Successfully!');
        
        // Update time every second
        setInterval(() => {{
            const timeElements = document.querySelectorAll('.info-value');
            if (timeElements.length > 2) {{
                timeElements[2].textContent = new Date().toLocaleTimeString();
            }}
        }}, 1000);
        
        // Add click effects
        document.querySelectorAll('.nav-card').forEach(card => {{
            card.addEventListener('click', (e) => {{
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    card.style.transform = 'translateY(-5px)';
                }}, 100);
            }});
        }});
    </script>
</body>
</html>
        """
    
    @app.route('/learn')
    def learn():
        if has_templates:
            try:
                return render_template('modern_learning.html')
            except:
                # Fallback to original template
                try:
                    return render_template('interactive_learning.html')
                except:
                    pass
        return '<h1>📚 Interactive Learning Module</h1><p>Advanced learning features coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/quiz')
    def quiz():
        if has_templates:
            try:
                return render_template('modern_quiz.html')
            except:
                # Fallback to original template
                try:
                    return render_template('quiz.html')
                except:
                    pass
        return '<h1>🧠 Quiz System</h1><p>Intelligent quiz system coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/progress')
    def progress():
        if has_templates:
            try:
                return render_template('modern_progress.html')
            except:
                try:
                    return render_template('progress_analytics.html')
                except:
                    pass
        return '<h1>📈 Progress Analytics</h1><p>Learning analytics dashboard coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/hardware')
    def hardware():
        if has_templates:
            try:
                return render_template('modern_hardware.html')
            except:
                try:
                    return render_template('hardware_control.html')
                except:
                    pass
        return '<h1>⚙️ Hardware Control</h1><p>Arduino and IoT integration coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/language-learning')
    def language_learning():
        """Language Learning Mode Route"""
        if has_templates:
            try:
                return render_template('language_learning.html')
            except Exception as e:
                print(f"Error loading language learning template: {e}")
        return '<h1>🎓 Language Learning Mode</h1><p>Interactive Tamil, English & Hindi learning coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/debate-mode')
    def debate_mode_route():
        """Debate Mode Route"""
        if has_templates:
            try:
                return render_template('debate_mode.html')
            except Exception as e:
                print(f"Error loading debate mode template: {e}")
        return '<h1>🎯 Debate Mode</h1><p>Interactive AI-powered debates and discussions coming soon!</p><a href="/">← Back to Dashboard</a>'
    
    @app.route('/api/test')
    def api_test():
        return jsonify({{
            'status': 'success',
            'message': '🤖 Laura-bot API is working perfectly!',
            'server': 'Flask + SocketIO',
            'timestamp': datetime.now().isoformat(),
            'features': {{
                'learning': 'active',
                'quiz': 'active', 
                'progress': 'active',
                'hardware': 'active',
                'voice': 'ready',
                'ai': 'ready'
            }},
            'endpoints': [
                '/api/test',
                '/api/progress_data',
                '/learn',
                '/quiz',
                '/progress',
                '/hardware'
            ]
        }})
    
    @app.route('/api/progress_data')
    def progress_data():
        return jsonify({{
            'success': True,
            'stats': {{
                'total_sessions': 25,
                'study_time_hours': 42.5,
                'avg_quiz_score': 91,
                'current_streak': 12,
                'subjects_mastered': 5
            }},
            'recent_activity': [
                {{'subject': 'Mathematics', 'score': 95, 'date': '2024-01-15'}},
                {{'subject': 'Science', 'score': 89, 'date': '2024-01-14'}},
                {{'subject': 'History', 'score': 93, 'date': '2024-01-13'}}
            ]
        }})
    
    @app.route('/api/translate', methods=['POST'])
    def translate_api():
        """Language Learning Translation API"""
        try:
            # Import language learning mode
            from translator.language_learning_mode import language_learner
            
            data = request.get_json()
            text = data.get('text', '').strip()
            source_lang = data.get('source_lang', '').lower()
            target_lang = data.get('target_lang', '').lower()
            
            if not text or not source_lang or not target_lang:
                return jsonify({
                    'error': 'Missing required fields: text, source_lang, target_lang'
                }), 400
            
            # Perform enhanced translation with learning features
            result = language_learner.translate_with_learning(text, source_lang, target_lang)
            
            return jsonify({
                'success': True,
                'translation': result.get('translation', ''),
                'pronunciation': result.get('pronunciation', ''),
                'grammar_note': result.get('grammar_note', ''),
                'cultural_context': result.get('cultural_context', ''),
                'difficulty_level': result.get('difficulty_level', 'beginner'),
                'source_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Translation API error: {e}")
            return jsonify({
                'error': f'Translation failed: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/start', methods=['POST'])
    def start_debate_api():
        """Start a new debate session"""
        try:
            # Import debate mode
            from ai.debate_mode import debate_mode
            
            data = request.get_json()
            topic = data.get('topic', '').strip()
            user_position = data.get('user_position', '').strip()
            ai_persona = data.get('ai_persona', 'balanced')
            
            result = debate_mode.start_debate(topic, user_position, ai_persona)
            
            return jsonify({
                'success': True,
                'debate_setup': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Start debate API error: {e}")
            return jsonify({
                'error': f'Failed to start debate: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/position', methods=['POST'])
    def set_debate_position_api():
        """Set user's debate position"""
        try:
            from ai.debate_mode import debate_mode
            
            data = request.get_json()
            position = data.get('position', '').strip()
            
            if not position:
                return jsonify({
                    'error': 'Missing required field: position'
                }), 400
            
            result = debate_mode.set_user_position(position)
            
            return jsonify({
                'success': True,
                'position_setup': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Set position API error: {e}")
            return jsonify({
                'error': f'Failed to set position: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/argument', methods=['POST'])
    def submit_argument_api():
        """Submit user argument and get AI counter-argument"""
        try:
            from ai.debate_mode import debate_mode
            
            data = request.get_json()
            argument = data.get('argument', '').strip()
            
            if not argument:
                return jsonify({
                    'error': 'Missing required field: argument'
                }), 400
            
            result = debate_mode.process_user_argument(argument)
            
            return jsonify({
                'success': True,
                'debate_response': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Submit argument API error: {e}")
            return jsonify({
                'error': f'Failed to process argument: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/end', methods=['POST'])
    def end_debate_api():
        """End current debate and get final evaluation"""
        try:
            from ai.debate_mode import debate_mode
            
            result = debate_mode.end_debate()
            
            return jsonify({
                'success': True,
                'final_evaluation': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"End debate API error: {e}")
            return jsonify({
                'error': f'Failed to end debate: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/suggestions')
    def debate_suggestions_api():
        """Get debate topic suggestions"""
        try:
            from ai.debate_mode import debate_mode
            
            category = request.args.get('category', '')
            result = debate_mode.get_debate_suggestions(category if category else None)
            
            return jsonify({
                'success': True,
                'suggestions': result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Debate suggestions API error: {e}")
            return jsonify({
                'error': f'Failed to get suggestions: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/stats')
    def debate_stats_api():
        """Get debate statistics"""
        try:
            from ai.debate_mode import debate_mode
            
            stats = debate_mode.get_debate_stats()
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Debate stats API error: {e}")
            return jsonify({
                'error': f'Failed to get stats: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/debate/status')
    def debate_status_api():
        """Get current debate status"""
        try:
            from ai.debate_mode import debate_mode
            
            status = debate_mode.get_current_status()
            
            return jsonify({
                'success': True,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Debate status API error: {e}")
            return jsonify({
                'error': f'Failed to get status: {str(e)}',
                'success': False
            }), 500

    @app.route('/api/language-stats')
    def language_stats_api():
        """Get language learning statistics"""
        try:
            from translator.language_learning_mode import language_learner
            
            stats = language_learner.get_learning_stats()
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Language stats API error: {e}")
            return jsonify({
                'error': f'Failed to get stats: {str(e)}',
                'success': False
            }), 500
    
    @app.route('/api/practice-suggestions')
    def practice_suggestions_api():
        """Get practice suggestions for language pair"""
        try:
            from translator.language_learning_mode import language_learner
            
            source_lang = request.args.get('source', '').lower()
            target_lang = request.args.get('target', '').lower()
            
            if not source_lang or not target_lang:
                return jsonify({
                    'error': 'Missing required parameters: source, target'
                }), 400
            
            language_pair = f"{source_lang}_{target_lang}"
            suggestions = language_learner.get_practice_suggestion(language_pair)
            
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'language_pair': language_pair,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Practice suggestions API error: {e}")
            return jsonify({
                'error': f'Failed to get suggestions: {str(e)}',
                'success': False
            }), 500
    
    # Hardware Socket.IO events
    @socketio.on('request_hardware_status')
    def handle_hardware_status():
        """Request current hardware status"""
        if hardware_controller:
            status = hardware_controller.get_status()
            emit('hardware_status', status)
        else:
            emit('hardware_status', {
                'connected': False,
                'hardware_status': {
                    'arduino': 'disconnected',
                    'serial': 'disconnected', 
                    'camera': 'disconnected',
                    'speech': 'disconnected'
                },
                'sensor_data': {},
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('request_sensor_data')
    def handle_sensor_data():
        """Request current sensor data"""
        if hardware_controller:
            sensor_data = hardware_controller.sensor_data
            sensor_data['timestamp'] = datetime.now().isoformat()
            emit('sensor_data', sensor_data)
        else:
            emit('sensor_data', {
                'distance': 50,
                'light_level': 75,
                'sound_level': 30,
                'current_gesture': None,
                'timestamp': datetime.now().isoformat()
            })
    
    @socketio.on('servo_control')
    def handle_servo_control(data):
        """Control servo motors"""
        servo = data.get('servo')
        angle = data.get('angle')
        
        if hardware_controller:
            success = hardware_controller.control_servo(servo, angle)
            emit('hardware_response', {
                'message': f'Servo {servo} moved to {angle}°' if success else f'Failed to control servo {servo}',
                'type': 'success' if success else 'error'
            })
        else:
            print(f"🎭 Simulated: Servo {servo} -> {angle}°")
            emit('hardware_response', {
                'message': f'Simulated: Servo {servo} moved to {angle}°',
                'type': 'info'
            })
    
    @socketio.on('servo_preset')
    def handle_servo_preset(data):
        """Move servos to preset position"""
        preset = data.get('preset')
        
        if hardware_controller:
            # Define preset positions
            presets = {
                'ready': {'head_pan': 90, 'head_tilt': 90, 'arm_left': 90, 'arm_right': 90},
                'greeting': {'head_pan': 90, 'head_tilt': 70, 'arm_left': 150, 'arm_right': 30},
                'thinking': {'head_pan': 45, 'head_tilt': 110, 'arm_left': 120, 'arm_right': 60},
                'celebration': {'head_pan': 90, 'head_tilt': 60, 'arm_left': 180, 'arm_right': 0}
            }
            
            if preset in presets:
                success_count = 0
                for servo, angle in presets[preset].items():
                    if hardware_controller.control_servo(servo, angle):
                        success_count += 1
                
                emit('hardware_response', {
                    'message': f'Moved to {preset} position',
                    'type': 'success'
                })
            else:
                emit('hardware_response', {
                    'message': f'Unknown preset: {preset}',
                    'type': 'error'
                })
        else:
            print(f"🎭 Simulated: Preset position {preset}")
            emit('hardware_response', {
                'message': f'Simulated: Moved to {preset} position',
                'type': 'info'
            })
    
    @socketio.on('led_control')
    def handle_led_control(data):
        """Control LED states"""
        led = data.get('led')
        state = data.get('state')
        
        if hardware_controller:
            success = hardware_controller.set_led(led, state)
            emit('hardware_response', {
                'message': f'LED {led} {"on" if state else "off"}' if success else f'Failed to control LED {led}',
                'type': 'success' if success else 'error'
            })
        else:
            print(f"🎭 Simulated: LED {led} -> {'ON' if state else 'OFF'}")
            emit('hardware_response', {
                'message': f'Simulated: LED {led} {"on" if state else "off"}',
                'type': 'info'
            })
    
    @socketio.on('led_pattern')
    def handle_led_pattern(data):
        """Control LED patterns"""
        pattern = data.get('pattern')
        
        if hardware_controller:
            # Implement LED patterns
            if pattern == 'blink':
                # Start blinking pattern
                emit('hardware_response', {
                    'message': 'Started blinking pattern',
                    'type': 'success'
                })
            elif pattern == 'off':
                hardware_controller.set_led('led_status', False)
                hardware_controller.set_led('led_eyes', False)
                emit('hardware_response', {
                    'message': 'All LEDs turned off',
                    'type': 'success'
                })
        else:
            print(f"🎭 Simulated: LED pattern {pattern}")
            emit('hardware_response', {
                'message': f'Simulated: LED pattern {pattern}',
                'type': 'info'
            })
    
    @socketio.on('movement_control')
    def handle_movement_control(data):
        """Control robot movement"""
        direction = data.get('direction')
        speed = data.get('speed', 50)
        
        if hardware_controller:
            success = hardware_controller.move_robot(direction, {'speed': speed})
            emit('hardware_response', {
                'message': f'Moving {direction} at {speed}% speed' if success else f'Movement failed',
                'type': 'success' if success else 'error'
            })
        else:
            print(f"🎭 Simulated: Move {direction} at {speed}% speed")
            emit('hardware_response', {
                'message': f'Simulated: Moving {direction}',
                'type': 'info'
            })
    
    @socketio.on('emergency_stop')
    def handle_emergency_stop():
        """Emergency stop all movement"""
        if hardware_controller:
            hardware_controller.move_robot('stop', {'emergency': True})
            emit('hardware_response', {
                'message': 'Emergency stop activated',
                'type': 'warning'
            })
        else:
            print("🎭 Simulated: Emergency stop")
            emit('hardware_response', {
                'message': 'Simulated: Emergency stop',
                'type': 'warning'
            })
    
    @socketio.on('speech_synthesis')
    def handle_speech_synthesis(data):
        """Text-to-speech"""
        text = data.get('text', '')
        
        if hardware_controller:
            success = hardware_controller.speak(text)
            emit('hardware_response', {
                'message': 'Speaking...' if success else 'Speech synthesis failed',
                'type': 'success' if success else 'error'
            })
        else:
            print(f"🎭 Simulated speech: {text}")
            emit('hardware_response', {
                'message': f'Simulated speech: {text}',
                'type': 'info'
            })
    
    @socketio.on('speech_recognition')
    def handle_speech_recognition(data):
        """Speech-to-text"""
        timeout = data.get('timeout', 5)
        
        if hardware_controller:
            recognized_text = hardware_controller.listen(timeout)
            emit('speech_recognized', {
                'text': recognized_text,
                'success': recognized_text is not None
            })
        else:
            print("🎭 Simulated speech recognition")
            emit('speech_recognized', {
                'text': 'Simulated speech input',
                'success': True
            })
    
    @socketio.on('speech_settings')
    def handle_speech_settings(data):
        """Update speech synthesis settings"""
        rate = data.get('rate', 200)
        volume = data.get('volume', 80)
        
        if hardware_controller and hardware_controller.tts_engine:
            hardware_controller.tts_engine.setProperty('rate', rate)
            hardware_controller.tts_engine.setProperty('volume', volume / 100.0)
            emit('hardware_response', {
                'message': f'Speech settings updated: {rate} WPM, {volume}% volume',
                'type': 'success'
            })
        else:
            print(f"🎭 Simulated: Speech rate {rate} WPM, volume {volume}%")
            emit('hardware_response', {
                'message': f'Simulated: Speech settings updated',
                'type': 'info'
            })
    
    @socketio.on('start_camera')
    def handle_start_camera():
        """Start camera feed"""
        if hardware_controller and hardware_controller.camera:
            emit('hardware_response', {
                'message': 'Camera started',
                'type': 'success'
            })
        else:
            print("🎭 Simulated: Camera started")
            emit('hardware_response', {
                'message': 'Simulated: Camera started',
                'type': 'info'
            })
    
    @socketio.on('stop_camera')
    def handle_stop_camera():
        """Stop camera feed"""
        emit('hardware_response', {
            'message': 'Camera stopped',
            'type': 'info'
        })
    
    @socketio.on('capture_image')
    def handle_capture_image():
        """Capture image from camera"""
        if hardware_controller and hardware_controller.camera:
            # Implement image capture
            emit('hardware_response', {
                'message': 'Image captured successfully',
                'type': 'success'
            })
        else:
            print("🎭 Simulated: Image captured")
            emit('hardware_response', {
                'message': 'Simulated: Image captured',
                'type': 'info'
            })
    
    @socketio.on('restart_hardware')
    def handle_restart_hardware():
        """Restart hardware connections"""
        global hardware_controller
        
        if HARDWARE_AVAILABLE:
            try:
                if hardware_controller:
                    hardware_controller.shutdown()
                
                hardware_controller = initialize_hardware()
                emit('hardware_response', {
                    'message': 'Hardware restarted successfully',
                    'type': 'success'
                })
            except Exception as e:
                emit('hardware_response', {
                    'message': f'Hardware restart failed: {str(e)}',
                    'type': 'error'
                })
        else:
            emit('hardware_response', {
                'message': 'Hardware not available for restart',
                'type': 'warning'
            })
    
    @socketio.on('run_diagnostics')
    def handle_run_diagnostics():
        """Run hardware diagnostics"""
        if hardware_controller:
            status = hardware_controller.get_status()
            connected_components = sum(1 for status in status['hardware_status'].values() if status == 'connected')
            total_components = len(status['hardware_status'])
            
            emit('diagnostics_complete', {
                'result': f'{connected_components}/{total_components} components connected',
                'details': status['hardware_status']
            })
        else:
            emit('diagnostics_complete', {
                'result': 'No hardware connected',
                'details': {}
            })
    
    # Standard SocketIO events
    @socketio.on('connect')
    def handle_connect():
        print('🔌 Client connected')
        emit('status_update', {
            'message': 'Connected to Laura-bot!',
            'timestamp': datetime.now().isoformat(),
            'server_status': 'online'
        })
        
        # Send initial hardware status
        if hardware_controller:
            status = hardware_controller.get_status()
            emit('hardware_status', status)
    
    @socketio.on('disconnect') 
    def handle_disconnect():
        print('🔌 Client disconnected')
    
    print("   ✅ All routes and handlers configured")
    
    print(f"\n🌐 Starting Laura-bot server...")
    print(f"   📍 URL: http://localhost:5555")
    print(f"   🎯 Main Dashboard: http://localhost:5555/")
    print(f"   📚 Learning: http://localhost:5555/learn")  
    print(f"   🧠 Quiz: http://localhost:5555/quiz")
    print(f"   📈 Progress: http://localhost:5555/progress")
    print(f"   ⚙️ Hardware: http://localhost:5555/hardware")
    print(f"   🔧 API Test: http://localhost:5555/api/test")
    print("=" * 60)
    print("✨ Laura-bot is ready! Opening browser...")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Try to open browser after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5555')
            print("🌐 Browser opened automatically")
        except:
            print("🌐 Please manually open: http://localhost:5555")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    socketio.run(
        app,
        host='0.0.0.0',
        port=5555,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )

except ImportError as e:
    print(f"\n❌ Import Error: {{e}}")
    print("💡 Please install required packages:")
    print("   pip install flask flask-socketio")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error starting Laura-bot: {{e}}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)