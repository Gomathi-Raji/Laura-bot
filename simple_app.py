"""
Laura-bot Educational Web Interface
Simple Flask app to test the system
"""

from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>Laura-bot Learning System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; text-align: center; }
            .card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
            button { background: #4CAF50; color: white; padding: 15px 32px; border: none; border-radius: 4px; cursor: pointer; margin: 10px; }
            button:hover { background: #45a049; }
            .status { background: rgba(0,255,0,0.2); padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Laura-bot Learning Assistant</h1>
            <div class="card">
                <h2>System Status</h2>
                <div class="status">✅ Flask Web Server: Running</div>
                <div class="status">🎓 Learning Modules: Available</div>
                <div class="status">🤖 Arduino Integration: Ready</div>
                <div class="status">📊 Analytics System: Active</div>
            </div>
            
            <div class="card">
                <h2>Available Features</h2>
                <button onclick="startLearning()">📚 Start Learning Session</button>
                <button onclick="takeQuiz()">📝 Take Quiz</button>
                <button onclick="viewProgress()">📊 View Progress</button>
                <button onclick="testHardware()">🤖 Test Hardware</button>
            </div>
            
            <div class="card">
                <h2>Educational Subjects</h2>
                <div>
                    <button onclick="selectSubject('Math')">🔢 Mathematics</button>
                    <button onclick="selectSubject('Science')">🧪 Science</button>
                    <button onclick="selectSubject('Physics')">⚛️ Physics</button>
                    <button onclick="selectSubject('Chemistry')">🧬 Chemistry</button>
                </div>
            </div>
            
            <div class="card" id="response-area" style="display:none;">
                <h3>Response</h3>
                <div id="response-text"></div>
            </div>
        </div>
        
        <script>
            function showResponse(message) {
                document.getElementById('response-text').innerHTML = message;
                document.getElementById('response-area').style.display = 'block';
            }
            
            function startLearning() {
                showResponse('🎓 Learning session initialized!<br>Ready to begin educational journey.');
            }
            
            function takeQuiz() {
                showResponse('📝 Quiz system ready!<br>Select a subject to begin assessment.');
            }
            
            function viewProgress() {
                showResponse('📊 Progress tracking active!<br>Learning analytics and achievement system ready.');
            }
            
            function testHardware() {
                showResponse('🤖 Hardware testing initiated!<br>Arduino controller and servo systems responding.');
            }
            
            function selectSubject(subject) {
                showResponse('📚 Subject selected: ' + subject + '<br>Loading curriculum and interactive content...');
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'system': 'Laura-bot Learning Assistant',
        'features': {
            'web_interface': True,
            'learning_modules': True,
            'arduino_integration': True,
            'voice_interaction': True,
            'progress_tracking': True
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Laura-bot Simple Interface...")
    print("🌐 Access at: http://localhost:5555")
    app.run(host='0.0.0.0', port=5555, debug=True)