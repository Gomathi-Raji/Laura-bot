#!/usr/bin/env python3
"""
Minimal Laura-bot Flask Test Server
"""

from flask import Flask, render_template, jsonify
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laura-bot Test Server</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .status { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
            a { color: #ffeb3b; text-decoration: none; margin: 10px; display: inline-block; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🤖 Laura-bot Flask Server is Running! ✨</h1>
        <div class="status">
            <p><strong>Status:</strong> ✅ Server Active</p>
            <p><strong>Port:</strong> 5555</p>
            <p><strong>Time:</strong> <script>document.write(new Date().toLocaleString())</script></p>
        </div>
        
        <h2>🚀 Available Features:</h2>
        <div>
            <a href="/test">🧪 Test API</a>
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/learn">📚 Learning</a>
            <a href="/progress">📈 Progress</a>
        </div>
        
        <div class="status">
            <p><em>Laura-bot Educational Platform - Ready for Learning!</em></p>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'Laura-bot API is working!',
        'server': 'Flask Development Server',
        'port': 5555
    })

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('enhanced_dashboard.html')
    except:
        return '<h1>Dashboard template not found - but server is working!</h1><a href="/">← Back to Home</a>'

@app.route('/learn')
def learn():
    try:
        return render_template('interactive_learning.html')
    except:
        return '<h1>Learning template not found - but server is working!</h1><a href="/">← Back to Home</a>'

@app.route('/progress')
def progress():
    try:
        return render_template('progress_analytics.html')
    except:
        return '<h1>Progress template not found - but server is working!</h1><a href="/">← Back to Home</a>'

if __name__ == '__main__':
    print("🚀 Starting Laura-bot Test Server...")
    print("📍 URL: http://localhost:5555")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5555, debug=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")