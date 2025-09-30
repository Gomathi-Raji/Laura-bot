print("Starting Laura-bot...")
import sys
print(f"Python version: {sys.version}")

try:
    from flask import Flask
    print("Flask imported successfully")
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <h1>🤖 Laura-bot Learning System</h1>
        <h2>System Status: Online ✅</h2>
        <p>Flask server is running successfully!</p>
        <div style="margin-top: 30px;">
            <h3>Available Features:</h3>
            <ul>
                <li>✅ Web Interface</li>
                <li>✅ Educational Modules</li>
                <li>✅ Arduino Integration (Simulation)</li>
                <li>✅ Progress Tracking</li>
                <li>✅ Voice Interaction</li>
            </ul>
        </div>
        <div style="margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 5px;">
            <h3>Next Steps:</h3>
            <p>1. Test learning modules</p>
            <p>2. Connect Arduino hardware</p>
            <p>3. Start learning session</p>
        </div>
        '''
    
    print("Routes configured")
    print("Starting Flask server on http://localhost:5555...")
    app.run(host='0.0.0.0', port=5555, debug=False)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()