from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Laura-bot is Running!</h1><p>Flask server active on port 5555</p>'

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5555, debug=True)