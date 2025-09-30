#!/usr/bin/env python3
"""
Laura-bot Hardware Test Script
Tests hardware integration and functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hardware_connection():
    """Test Arduino hardware connection"""
    print("🔧 Testing Hardware Connection...")
    
    try:
        from arduino.educational_controller import ArduinoEducationalController
        controller = ArduinoEducationalController()
        
        if hasattr(controller, 'connected') and controller.connected:
            print("✅ Hardware Controller: Connected")
            return True
        else:
            print("⚠️ Hardware Controller: Simulation Mode")
            return False
    except Exception as e:
        print(f"❌ Hardware Controller Error: {e}")
        return False

def test_voice_modules():
    """Test voice recognition and speech modules"""
    print("\n🎙️ Testing Voice Modules...")
    
    try:
        from voice.speaker import speak, board
        from voice.listener import listen
        
        print("✅ Voice Speaker: Available")
        print("✅ Voice Listener: Available")
        
        # Test speaker
        speak("Hardware test successful")
        print("✅ Text-to-Speech: Working")
        
        # Test hardware board connection
        if board:
            print("✅ Arduino Board: Connected")
            return True
        else:
            print("⚠️ Arduino Board: Not connected")
            return False
            
    except Exception as e:
        print(f"❌ Voice Module Error: {e}")
        return False

def test_ai_modules():
    """Test AI integration"""
    print("\n🤖 Testing AI Modules...")
    
    try:
        from ai.gemini_ai import get_response, get_tutor_response, generate_quiz
        
        # Test basic AI response
        response = get_response("Hello, this is a test")
        print(f"✅ AI Response: {response[:50]}...")
        
        # Test tutor response
        tutor_response = get_tutor_response("What is 2+2?", "mathematics")
        print(f"✅ AI Tutor: {tutor_response[:50]}...")
        
        # Test quiz generation
        quiz = generate_quiz("mathematics", "easy")
        print(f"✅ Quiz Generation: {quiz.get('question', 'Generated')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Module Error: {e}")
        return False

def test_learning_modules():
    """Test learning and education modules"""
    print("\n📚 Testing Learning Modules...")
    
    try:
        from education_modules import get_education_module, list_available_subjects
        from learning_tracker import LearningTracker
        
        # Test subjects
        subjects = list_available_subjects()
        print(f"✅ Available Subjects: {subjects}")
        
        # Test education module
        math_module = get_education_module("Mathematics")
        if math_module:
            print("✅ Math Module: Loaded")
        else:
            print("⚠️ Math Module: Not available")
        
        # Test learning tracker
        tracker = LearningTracker()
        print("✅ Learning Tracker: Initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning Module Error: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\n🌐 Testing Flask Application...")
    
    try:
        import flask_app
        print("✅ Flask App: Imports successfully")
        
        # Test if app can start (without actually running)
        app = flask_app.app
        if app:
            print("✅ Flask App: Created successfully")
            print(f"✅ Registered Routes: {len(app.url_map._rules)} routes")
            return True
        else:
            print("❌ Flask App: Failed to create")
            return False
            
    except Exception as e:
        print(f"❌ Flask App Error: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        ('flask', 'Flask web framework'),
        ('flask_socketio', 'SocketIO for real-time communication'),
        ('pygame', 'Audio playback'),
        ('gtts', 'Google Text-to-Speech'),
        ('speech_recognition', 'Speech recognition'),
        ('pyfirmata', 'Arduino communication'),
        ('sqlite3', 'Database (built-in)'),
    ]
    
    results = []
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
            results.append(True)
        except ImportError:
            print(f"❌ {module}: {description} - NOT INSTALLED")
            results.append(False)
        except Exception as e:
            print(f"⚠️ {module}: {description} - {e}")
            results.append(False)
    
    return all(results)

def run_comprehensive_test():
    """Run all hardware and system tests"""
    print("🚀 Laura-bot Comprehensive Hardware Test")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_dependencies())
    test_results.append(test_flask_app())
    test_results.append(test_learning_modules())
    test_results.append(test_ai_modules())
    test_results.append(test_voice_modules())
    test_results.append(test_hardware_connection())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Laura-bot is ready to use.")
        return True
    elif passed >= total * 0.7:
        print("⚠️ Most tests passed. Laura-bot should work with limited functionality.")
        return True
    else:
        print("❌ Multiple test failures. Laura-bot may have issues.")
        return False

if __name__ == "__main__":
    print("Starting Laura-bot Hardware Test...")
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 Recommendation: You can start the Flask app with:")
        print("   python flask_app.py")
        print("\n🌐 Then visit: http://localhost:5000")
    else:
        print("\n🔧 Recommendation: Fix the failing components before starting.")
        print("   Install missing dependencies with: pip install -r requirements.txt")
    
    sys.exit(0 if success else 1)