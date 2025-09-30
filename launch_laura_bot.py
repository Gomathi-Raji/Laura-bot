#!/usr/bin/env python3
"""
Laura-bot Flask Application Launcher
Simple launcher script with comprehensive error handling
"""

import sys
import os
import traceback
from datetime import datetime

def main():
    """Main launcher function with error handling"""
    print("🚀 Starting Laura-bot Flask Application")
    print("=" * 50)
    print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("=" * 50)
    
    try:
        # Test imports first
        print("🔍 Testing imports...")
        
        print("   - Importing Flask...")
        from flask import Flask, render_template, request, jsonify
        print("   ✅ Flask imported successfully")
        
        print("   - Importing Flask-SocketIO...")
        from flask_socketio import SocketIO, emit
        print("   ✅ Flask-SocketIO imported successfully")
        
        print("   - Importing datetime...")
        from datetime import datetime
        print("   ✅ datetime imported successfully")
        
        print("🏗️ Creating Flask application...")
        
        # Create Flask app
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'laura-bot-secret-key-2024'
        print("   ✅ Flask app created")
        
        # Initialize SocketIO
        socketio = SocketIO(app, cors_allowed_origins="*")
        print("   ✅ SocketIO initialized")
        
        # Define routes
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
        
        @socketio.on('connect')
        def handle_connect():
            print('🔌 Client connected')
            emit('status_update', {
                'message': 'Connected to Laura-bot!',
                'timestamp': datetime.now().isoformat()
            })
        
        print("   ✅ Routes and handlers defined")
        
        # Check templates directory
        templates_dir = os.path.join(os.getcwd(), 'templates')
        if not os.path.exists(templates_dir):
            print(f"❌ Templates directory not found: {templates_dir}")
            return False
        
        print(f"   ✅ Templates directory found: {templates_dir}")
        
        # List template files
        template_files = os.listdir(templates_dir)
        print(f"   📄 Template files: {template_files}")
        
        # Check static directory
        static_dir = os.path.join(os.getcwd(), 'static')
        if os.path.exists(static_dir):
            print(f"   ✅ Static directory found: {static_dir}")
        else:
            print(f"   ⚠️ Static directory not found: {static_dir} (optional)")
        
        print("\n🌐 Starting Flask development server...")
        print("   📍 URL: http://localhost:5555")
        print("   🔧 Debug Mode: Enabled")
        print("   ⚡ Real-time features: Enabled")
        print("=" * 50)
        print("🎯 Available routes:")
        print("   • Main Dashboard: http://localhost:5555/")
        print("   • Interactive Learning: http://localhost:5555/learn")
        print("   • Quiz System: http://localhost:5555/quiz")
        print("   • Progress Analytics: http://localhost:5555/progress")
        print("   • Hardware Control: http://localhost:5555/hardware")
        print("=" * 50)
        print("✨ Laura-bot is ready! Open your browser and navigate to the URLs above.")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Please ensure Flask and Flask-SocketIO are installed:")
        print("   pip install flask flask-socketio")
        return False
        
    except FileNotFoundError as e:
        print(f"❌ File Not Found: {e}")
        print("💡 Please ensure you're running this script from the Laura-bot directory")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("🔍 Full error traceback:")
        traceback.print_exc()
        return False
    
    finally:
        print("\n🛑 Laura-bot server stopped")
        print(f"📅 Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        print("👋 Thank you for using Laura-bot!")