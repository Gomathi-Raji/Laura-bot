import os

# Disable Streamlit telemetry before importing streamlit
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false' 
os.environ['STREAMLIT_CLIENT_TOOLBAR_MODE'] = 'minimal'

import streamlit as st
import subprocess
import threading
import time
from datetime import datetime
import webbrowser
import speech_recognition as sr
from PIL import Image
import json
import queue

# Import your existing modules
from voice.speaker import speak
from voice.listener import listen
from ai.gemini_ai import get_response, get_tutor_response, generate_quiz, generate_explanation, generate_flashcard
from tasks.general_tasks import execute_command
from translator.speech_input import recognize_speech
from translator.translator_engine import translate_tamil_to_hindi
from translator.speech_output import speak_text

# Import new tutor modules
try:
    from learning_tracker import learning_tracker, start_session, end_session, record_quiz, get_stats
    TUTOR_MODE_AVAILABLE = True
except ImportError:
    TUTOR_MODE_AVAILABLE = False
    st.warning("⚠️ Learning tracker not available. Some tutor features may be limited.")

# Configure Streamlit page
st.set_page_config(
    page_title="🤖 Zara Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_log' not in st.session_state:
    st.session_state.conversation_log = []
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Standby"
if 'system_status' not in st.session_state:
    st.session_state.system_status = "Ready"
if 'tutor_mode' not in st.session_state:
    st.session_state.tutor_mode = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Student"
if 'api_status' not in st.session_state:
    st.session_state.api_status = "online"  # online, offline, limited
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'quiz_in_progress' not in st.session_state:
    st.session_state.quiz_in_progress = False
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}

# Functions - Define these first before they are called
def log_conversation(role, message):
    """Add message to conversation log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.conversation_log.append({
        'timestamp': timestamp,
        'role': role,
        'message': message
    })
    
    # Also log to file
    log_path = os.path.join(os.getcwd(), "conversation_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        full_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{full_timestamp}] {role}: {message}\n")

def start_voice_listening():
    """Start voice recognition in a separate thread"""
    st.session_state.is_listening = True
    st.session_state.system_status = "Listening"
    st.session_state.current_mode = "Voice Input"
    
    def listen_thread():
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
            
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10)
            
            command = recognizer.recognize_google(audio)
            log_conversation("User", command)
            
            st.session_state.system_status = "Processing"
            process_voice_command(command)
            
        except sr.WaitTimeoutError:
            st.session_state.system_status = "Ready"
            st.warning("⏰ Listening timeout. Please try again.")
        except Exception as e:
            st.session_state.system_status = "Error"
            st.error(f"❌ Error: {e}")
        finally:
            st.session_state.is_listening = False
            st.session_state.current_mode = "Standby"
    
    threading.Thread(target=listen_thread, daemon=True).start()

def stop_voice_listening():
    """Stop voice recognition"""
    st.session_state.is_listening = False
    st.session_state.system_status = "Ready"
    st.session_state.current_mode = "Standby"

def process_voice_command(command):
    """Process voice command and update UI"""
    st.session_state.system_status = "Processing"
    
    try:
        # Process the command using existing logic
        response = process_command_logic(command)
        log_conversation("Assistant", response)
        
        # Speak the response
        speak(response)
        
        st.session_state.system_status = "Ready"
        st.success(f"✅ Processed: {command}")
        
    except Exception as e:
        st.session_state.system_status = "Error"
        st.error(f"❌ Error processing command: {e}")

def process_text_command(command):
    """Process text command"""
    log_conversation("User", command)
    
    try:
        response = process_command_logic(command)
        log_conversation("Assistant", response)
        st.success(f"✅ Processed: {command}")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {e}")

def process_command_logic(command):
    """Main command processing logic"""
    if not command:
        return "No command received."
    
    # Check if in tutor mode first
    if st.session_state.tutor_mode:
        return handle_tutor_command(command)
    
    # Tutor mode activation
    if any(kw in command.lower() for kw in ["tutor", "learn", "study", "teach", "quiz", "explain", "கற்பிக்க", "படிக்க"]):
        st.session_state.tutor_mode = True
        st.session_state.current_mode = "Personal Tutor"
        return "🎓 Personal tutor mode activated! I'm here to help you learn. What subject would you like to study?"
    
    # Gesture command
    if any(kw in command.lower() for kw in ["gesture", "கை சைகை", "open gesture", "start gesture"]):
        st.session_state.current_mode = "Gesture Recognition"
        return open_gesture_window()
    
    # GIF display command
    if any(kw in command.lower() for kw in ["gif", "show gif", "display gif", "GIF காட்டு", "gif காட்டு"]):
        st.session_state.current_mode = "GIF Display"
        return "GIF display mode activated"
    
    # Spotify/music command
    if any(kw in command.lower() for kw in ["play song", "play music", "spotify", "பாடல் இசை", "இசை இசை"]):
        st.session_state.current_mode = "Music Player"
        return handle_music_command(command)
    
    # Direct song search
    if "play" in command.lower() and len(command.split()) > 1:
        parts = command.lower().split("play", 1)
        if len(parts) > 1:
            song_name = parts[1].strip()
            if song_name:
                return search_and_play_song_no_auth(song_name)
    
    # Translator command
    if any(kw in command.lower() for kw in ["translator", "translate", "மொழிபெயர்ப்பு", "tamil to hindi"]):
        st.session_state.current_mode = "Translator"
        return "Translator mode activated"
    
    # General task command
    if execute_command(command):
        return "General task executed successfully"
    
    # Use Gemini AI for other queries
    st.session_state.current_mode = "AI Chat"
    return get_response(command)

def handle_music_request():
    """Handle music player request"""
    st.session_state.current_mode = "Music Player"
    song_name = st.text_input("🎵 Enter song name:", key="song_input")
    if st.button("Search & Play", key="play_song"):
        if song_name:
            result = search_and_play_song_no_auth(song_name)
            log_conversation("User", f"Play: {song_name}")
            log_conversation("Assistant", result)
            st.success(f"🎵 Searching for: {song_name}")

def handle_gesture_request():
    """Handle gesture recognition request"""
    st.session_state.current_mode = "Gesture Recognition" 
    result = open_gesture_window()
    log_conversation("User", "Open gesture recognition")
    log_conversation("Assistant", result)

def handle_translator_request():
    """Handle translator request"""
    st.session_state.current_mode = "Multi-Language Translator"
    st.info("🌍 Multi-language translator activated. Supports Tamil, Telugu, Hindi & English translations.")
    
    # Language selection interface
    st.markdown("#### Select Translation Language Pair:")
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox("From:", ["Tamil", "Telugu", "Hindi", "English"], key="source_lang")
    with col2:
        target_lang = st.selectbox("To:", ["Hindi", "English", "Tamil", "Telugu"], key="target_lang")
    
    if st.button("Start Translation", key="start_translation"):
        st.success(f"🌍 {source_lang} ➡️ {target_lang} translation mode activated!")
        st.info("Use voice input to start translating or type your text below.")
        
        text_to_translate = st.text_area("Or type text to translate:", key="translate_text")
        if st.button("Translate Text", key="translate_button") and text_to_translate:
            # This would call the translation function
            st.success(f"Translating: {text_to_translate}")
            # result = translate_text(text_to_translate, source_lang.lower(), target_lang.lower())
            # st.write(f"Translation: {result}")

def handle_gif_request():
    """Handle GIF display request"""
    st.session_state.current_mode = "GIF Display"
    st.info("🎬 GIF display mode activated. Say trigger words like 'hello', 'thank you', 'yes', 'no'")


def handle_tutor_command(command):
    """Handle tutor mode commands"""
    command_lower = command.lower()
    
    # Exit tutor mode
    if any(kw in command_lower for kw in ["exit tutor", "stop tutor", "normal mode", "வெளியேறு"]):
        if st.session_state.current_session_id and TUTOR_MODE_AVAILABLE:
            end_session(st.session_state.current_session_id)
            st.session_state.current_session_id = None
        st.session_state.tutor_mode = False
        st.session_state.current_mode = "Standby"
        return "👋 Exited tutor mode. I'm back to general assistant mode!"
    
    # Quiz commands
    if any(kw in command_lower for kw in ["quiz", "test", "exam", "வினாடி வினா"]):
        return handle_quiz_request(command)
    
    # Explanation commands  
    if any(kw in command_lower for kw in ["explain", "what is", "tell me about", "விளக்கம்"]):
        return handle_explanation_request(command)
    
    # Study session commands
    if any(kw in command_lower for kw in ["start study", "begin lesson", "படிப்பு தொடங்க"]):
        return handle_study_session_request(command)
    
    # Progress commands
    if any(kw in command_lower for kw in ["progress", "stats", "score", "முன்னேற்றம்"]):
        return handle_progress_request()
    
    # Default: treat as educational query
    subject = extract_subject_from_command(command)
    return get_tutor_response(command, subject, "Interactive learning session")


def handle_quiz_request(command):
    """Handle quiz generation and management"""
    if not TUTOR_MODE_AVAILABLE:
        return "📚 Quiz feature requires learning tracker. Please check installation."
    
    # Extract subject and topic from command
    subject = extract_subject_from_command(command)
    topic = extract_topic_from_command(command)
    
    if not subject:
        return "🤔 What subject would you like to be quizzed on? (Math, Science, Languages, History, etc.)"
    
    # Generate quiz
    try:
        quiz = generate_quiz(subject, topic or subject, difficulty=2, num_questions=5)
        st.session_state.current_quiz = quiz
        st.session_state.quiz_in_progress = True
        st.session_state.quiz_score = {"correct": 0, "total": len(quiz.get("questions", []))}
        
        if quiz and "questions" in quiz:
            first_question = quiz["questions"][0]
            return format_quiz_question(first_question, 1, len(quiz["questions"]))
        else:
            return f"📝 Generated a quiz on {subject} - {topic}. Let's start!"
            
    except Exception as e:
        return f"❌ Error generating quiz: {e}"


def handle_explanation_request(command):
    """Handle explanation requests"""
    # Extract topic from command
    topic = command.lower().replace("explain", "").replace("what is", "").replace("tell me about", "").strip()
    subject = extract_subject_from_command(command)
    
    if not topic:
        return "🤔 What would you like me to explain?"
    
    try:
        explanation = generate_explanation(topic, subject, "beginner")
        return f"📚 **Explanation of {topic.title()}:**\n\n{explanation}"
    except Exception as e:
        return f"❌ Error generating explanation: {e}"


def handle_study_session_request(command):
    """Handle study session start"""
    if not TUTOR_MODE_AVAILABLE:
        return "📚 Study sessions require learning tracker. Please check installation."
    
    subject = extract_subject_from_command(command)
    topic = extract_topic_from_command(command)
    
    if not subject:
        return "📖 What subject would you like to study today?"
    
    try:
        session_id = start_session(st.session_state.current_user, subject, topic or subject, 2)
        st.session_state.current_session_id = session_id
        return f"📚 Started study session: {subject} - {topic or subject}. Let's learn together!"
    except Exception as e:
        return f"❌ Error starting study session: {e}"


def handle_progress_request():
    """Handle progress and statistics requests"""
    if not TUTOR_MODE_AVAILABLE:
        return "📊 Progress tracking requires learning tracker. Please check installation."
    
    try:
        stats = get_stats(st.session_state.current_user)
        if "error" in stats:
            return "📊 No learning data available yet. Start studying to see your progress!"
        
        return format_progress_stats(stats)
    except Exception as e:
        return f"❌ Error retrieving progress: {e}"


def extract_subject_from_command(command):
    """Extract subject from command"""
    subjects = {
        "math": ["math", "mathematics", "algebra", "geometry", "calculus", "கணிதம்"],
        "science": ["science", "physics", "chemistry", "biology", "அறிவியல்"],
        "english": ["english", "grammar", "literature", "writing", "ஆங்கிலம்"],
        "history": ["history", "historical", "வரலாறு"],
        "geography": ["geography", "location", "countries", "புவியியல்"],
        "languages": ["tamil", "hindi", "language", "மொழி"],
        "computer": ["computer", "programming", "coding", "கம்ப்யூட்டர்"]
    }
    
    command_lower = command.lower()
    for subject, keywords in subjects.items():
        if any(keyword in command_lower for keyword in keywords):
            return subject.title()
    
    return ""


def extract_topic_from_command(command):
    """Extract topic from command"""
    # Simple topic extraction - could be enhanced
    common_topics = {
        "algebra", "geometry", "fractions", "equations", "physics", "chemistry", 
        "grammar", "vocabulary", "reading", "writing", "history", "geography"
    }
    
    command_lower = command.lower()
    for topic in common_topics:
        if topic in command_lower:
            return topic.title()
    
    return ""


def format_quiz_question(question, current_num, total_num):
    """Format quiz question for display"""
    formatted = f"❓ **Question {current_num}/{total_num}:**\n\n"
    formatted += f"**{question.get('question', 'Question not available')}**\n\n"
    
    options = question.get('options', [])
    for option in options:
        formatted += f"{option}\n"
    
    formatted += "\n💭 Reply with A, B, C, or D for your answer."
    return formatted


def format_progress_stats(stats):
    """Format progress statistics for display"""
    if not stats or "error" in stats:
        return "📊 No progress data available yet."
    
    formatted = f"📊 **Learning Progress for {stats.get('user_name', 'Student')}:**\n\n"
    formatted += f"🎯 **Total Study Sessions:** {stats.get('total_sessions', 0)}\n"
    formatted += f"⏰ **Total Study Time:** {stats.get('total_time_hours', 0)} hours\n"
    formatted += f"📚 **Subjects Studied:** {', '.join(stats.get('subjects_studied', []))}\n"
    formatted += f"🏆 **Average Quiz Score:** {stats.get('average_quiz_score', 0):.1f}%\n"
    formatted += f"🔥 **Current Streak:** {stats.get('current_streak', 0)} days\n"
    formatted += f"⭐ **Best Streak:** {stats.get('best_streak', 0)} days\n"
    
    weak_topics = stats.get('weak_topics', [])
    strong_topics = stats.get('strong_topics', [])
    
    if weak_topics:
        formatted += f"\n📝 **Topics to Focus On:** {', '.join(weak_topics)}\n"
    if strong_topics:
        formatted += f"💪 **Strong Topics:** {', '.join(strong_topics)}\n"
    
    return formatted

def open_gesture_window():
    """Open gesture recognition window"""
    try:
        gesture_script_path = os.path.join(os.getcwd(), "gesture", "gesture.py")
        if os.path.exists(gesture_script_path):
            subprocess.Popen(["python", gesture_script_path])
            return "Gesture recognition window opened successfully"
        else:
            return "Gesture recognition file not found"
    except Exception as e:
        return f"Failed to open gesture window: {e}"

def search_and_play_song_no_auth(song_query):
    """Search and play song without authentication"""
    try:
        search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        webbrowser.open(search_url)
        return f"Opened Spotify search for: {song_query}"
    except Exception as e:
        return f"Error opening Spotify: {e}"

def handle_music_command(command):
    """Handle music-related commands"""
    return "Music player activated. Opening Spotify search..."

def export_conversation_log():
    """Export conversation log to JSON"""
    try:
        export_data = {
            'export_time': datetime.now().isoformat(),
            'conversation': st.session_state.conversation_log
        }
        
        filename = f"zara_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        st.success(f"📁 Conversation exported to: {filename}")
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    .status-ready { background-color: #d4edda; border: 1px solid #c3e6cb; }
    .status-listening { background-color: #fff3cd; border: 1px solid #ffeaa7; }
    .status-processing { background-color: #cce5ff; border: 1px solid #74b9ff; }
    .status-error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
    
    .conversation-bubble {
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    .assistant-bubble {
        background-color: #f3e5f5;
        margin-right: auto;
        text-align: left;
    }
    
    .feature-button {
        width: 100%;
        margin: 0.3rem 0;
        padding: 0.8rem;
        font-size: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Zara Voice Assistant</h1>
    <p>Your Intelligent Tamil Voice Assistant with Multi-Modal Capabilities</p>
</div>
""", unsafe_allow_html=True)

# Create main layout
col1, col2, col3 = st.columns([1, 2, 1])

# Left Sidebar - Controls
with col1:
    st.markdown("### 🎛️ Controls")
    
    # System Status
    status_color = {
        "Ready": "status-ready",
        "Listening": "status-listening", 
        "Processing": "status-processing",
        "Error": "status-error"
    }
    
    # API Status Indicator
    api_indicators = {
        "online": "🟢 Online",
        "offline": "🔴 Offline", 
        "limited": "🟡 Limited"
    }
    
    st.markdown(f"""
    <div class="status-card {status_color.get(st.session_state.system_status, 'status-ready')}">
        <strong>Status:</strong> {st.session_state.system_status}<br>
        <strong>AI Service:</strong> {api_indicators.get(st.session_state.api_status, '🟢 Online')}<br>
        <strong>Mode:</strong> {st.session_state.current_mode}
    </div>
    """, unsafe_allow_html=True)
    
    # Voice Control
    st.markdown("#### 🎤 Voice Control")
    if st.button("🎙️ Start Listening", key="start_listening", help="Start voice recognition"):
        start_voice_listening()
    
    if st.button("🛑 Stop Listening", key="stop_listening", help="Stop voice recognition"):
        stop_voice_listening()
    
    # Tutor Mode Toggle
    st.markdown("#### 🎓 Learning Mode")
    tutor_toggle = st.checkbox("Enable Personal Tutor", value=st.session_state.tutor_mode, key="tutor_toggle")
    if tutor_toggle != st.session_state.tutor_mode:
        st.session_state.tutor_mode = tutor_toggle
        if tutor_toggle:
            st.session_state.current_mode = "Personal Tutor"
            st.success("🎓 Personal tutor activated!")
        else:
            if st.session_state.current_session_id and TUTOR_MODE_AVAILABLE:
                end_session(st.session_state.current_session_id)
                st.session_state.current_session_id = None
            st.session_state.current_mode = "Standby"
            st.info("👋 Returned to general assistant mode")
        st.rerun()
    
    # Tutor-specific controls
    if st.session_state.tutor_mode:
        st.markdown("##### 📚 Learning Controls")
        
        # User name input
        user_name = st.text_input("👤 Your Name:", value=st.session_state.current_user, key="user_name_input")
        if user_name != st.session_state.current_user:
            st.session_state.current_user = user_name
        
        # Subject selection
        subjects = ["Math", "Science", "English", "History", "Geography", "Languages", "Computer Science"]
        selected_subject = st.selectbox("📖 Subject:", ["Select..."] + subjects, key="subject_select")
        
        # Difficulty level
        difficulty = st.slider("🎯 Difficulty Level:", 1, 5, 2, key="difficulty_slider")
        
        # Learning action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Start Quiz", key="start_quiz_btn", help="Generate a quiz"):
                if selected_subject != "Select...":
                    command = f"quiz me on {selected_subject}"
                    response = handle_tutor_command(command)
                    log_conversation("User", command)
                    log_conversation("Assistant", response)
                    st.rerun()
                else:
                    st.warning("Please select a subject first!")
        
        with col_b:
            if st.button("💡 Get Explanation", key="explanation_btn", help="Get topic explanation"):
                if selected_subject != "Select...":
                    topic = st.text_input("What topic to explain?", key="topic_input")
                    if topic:
                        command = f"explain {topic} in {selected_subject}"
                        response = handle_tutor_command(command)
                        log_conversation("User", command)
                        log_conversation("Assistant", response)
                        st.rerun()
        
        # Progress tracking
        if TUTOR_MODE_AVAILABLE:
            if st.button("📊 View Progress", key="progress_btn", help="Show learning statistics"):
                response = handle_progress_request()
                log_conversation("User", "Show my progress")
                log_conversation("Assistant", response)
                st.rerun()
        
        # Session management
        if st.session_state.current_session_id:
            st.success(f"📚 Study session active")
            if st.button("⏹️ End Session", key="end_session_btn"):
                if TUTOR_MODE_AVAILABLE:
                    end_session(st.session_state.current_session_id)
                st.session_state.current_session_id = None
                st.success("Session ended!")
                st.rerun()
        else:
            if st.button("📖 Start Study Session", key="start_session_btn", help="Begin tracked learning session"):
                if selected_subject != "Select...":
                    command = f"start study session for {selected_subject}"
                    response = handle_tutor_command(command)
                    log_conversation("User", command)
                    log_conversation("Assistant", response)
                    st.rerun()
    
    # Feature Buttons
    st.markdown("#### 🚀 Quick Actions")
    
    if st.button("🎵 Play Music", key="music", help="Open music player"):
        handle_music_request()
    
    if st.button("🤲 Gesture Recognition", key="gesture", help="Open gesture window"):
        handle_gesture_request()
    
    if st.button("🌍 Translator", key="translator", help="Start Tamil-Hindi translator"):
        handle_translator_request()
    
    if st.button("🎬 GIF Display", key="gif", help="Show GIF animations"):
        handle_gif_request()
    
    # Manual Text Input
    st.markdown("#### ✍️ Text Input")
    text_input = st.text_input("Type your command:", placeholder="Enter command manually...")
    if st.button("Send", key="send_text"):
        if text_input:
            process_text_command(text_input)

# Middle Column - Conversation
with col2:
    # Tutor Mode Dashboard
    if st.session_state.tutor_mode:
        st.markdown("### 🎓 Personal Learning Dashboard")
        
        # Current session status
        dashboard_col1, dashboard_col2, dashboard_col3 = st.columns(3)
        with dashboard_col1:
            if st.session_state.current_session_id:
                st.metric("📚 Study Session", "Active", delta="In Progress")
            else:
                st.metric("📚 Study Session", "Inactive", delta="Ready to Start")
        
        with dashboard_col2:
            if st.session_state.quiz_in_progress:
                st.metric("📝 Quiz Status", "In Progress", delta=f"Q{st.session_state.current_question}/{st.session_state.total_questions}")
            else:
                st.metric("📝 Quiz Status", "Available", delta="Ready")
        
        with dashboard_col3:
            st.metric("👤 Learning Mode", st.session_state.current_mode, delta="Active")
        
        # Progress visualization (if tracking available)
        if TUTOR_MODE_AVAILABLE and st.session_state.current_user:
            try:
                from learning_tracker import LearningTracker
                tracker = LearningTracker()
                
                # Get user stats
                user_stats = tracker.get_user_stats(st.session_state.current_user)
                if user_stats:
                    st.markdown("#### 📊 Your Learning Statistics")
                    
                    stats_col_a, stats_col_b, stats_col_c, stats_col_d = st.columns(4)
                    with stats_col_a:
                        st.metric("🎯 Total Sessions", user_stats.get('total_sessions', 0))
                    with stats_col_b:
                        st.metric("⏰ Study Time", f"{user_stats.get('total_time', 0):.1f} min")
                    with stats_col_c:
                        st.metric("📝 Quizzes Taken", user_stats.get('quizzes_completed', 0))
                    with stats_col_d:
                        score = user_stats.get('average_score', 0)
                        st.metric("📈 Avg Score", f"{score:.1f}%")
                    
                    # Subject breakdown
                    if 'subject_stats' in user_stats:
                        st.markdown("##### 📚 Subject Progress")
                        subject_data = user_stats['subject_stats']
                        if subject_data:
                            try:
                                import pandas as pd
                                df = pd.DataFrame.from_dict(subject_data, orient='index')
                                if not df.empty and 'sessions' in df.columns:
                                    st.bar_chart(df['sessions'])
                            except ImportError:
                                st.info("Install pandas for enhanced progress visualization")
            except Exception as e:
                st.info("📊 Progress tracking will be available once you start learning!")
        
        st.markdown("---")
    
    st.markdown("### 💬 Conversation")
    
    # Conversation Display
    conversation_container = st.container()
    with conversation_container:
        if st.session_state.conversation_log:
            for entry in st.session_state.conversation_log[-10:]:  # Show last 10 messages
                timestamp = entry.get('timestamp', '')
                role = entry.get('role', '')
                message = entry.get('message', '')
                
                if role == "User":
                    st.markdown(f"""
                    <div class="conversation-bubble user-bubble">
                        <small>{timestamp}</small><br>
                        <strong>You:</strong> {message}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Enhanced display for tutor mode
                    if st.session_state.tutor_mode:
                        # Special formatting for quiz questions
                        if "Quiz Question" in message or any(opt in message for opt in ["A)", "B)", "C)", "D)"]):
                            st.markdown(f"""
                            <div class="conversation-bubble assistant-bubble" style="border-left: 4px solid #ff6b6b;">
                                <small>{timestamp}</small><br>
                                <strong>🎓 Laura (Tutor):</strong> {message}
                                <br><small><em>💡 Tip: Answer with 'A', 'B', 'C', or 'D' followed by your choice</em></small>
                            </div>
                            """, unsafe_allow_html=True)
                        # Special formatting for explanations
                        elif "Explanation:" in message or "Let me explain" in message:
                            st.markdown(f"""
                            <div class="conversation-bubble assistant-bubble" style="border-left: 4px solid #4ecdc4;">
                                <small>{timestamp}</small><br>
                                <strong>📚 Laura (Tutor):</strong> {message}
                            </div>
                            """, unsafe_allow_html=True)
                        # Regular tutor messages
                        else:
                            st.markdown(f"""
                            <div class="conversation-bubble assistant-bubble" style="border-left: 4px solid #45b7d1;">
                                <small>{timestamp}</small><br>
                                <strong>🎓 Laura (Tutor):</strong> {message}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="conversation-bubble assistant-bubble">
                            <small>{timestamp}</small><br>
                            <strong>Laura:</strong> {message}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("🤖 Hi! I'm Zara. Start a conversation by clicking 'Start Listening' or typing a command.")
    
    # Live transcription area
    if st.session_state.is_listening:
        st.markdown("### 🎤 Live Transcription")
        transcription_placeholder = st.empty()
        transcription_placeholder.info("🎧 Listening... Speak now!")

# Right Column - System Info
with col3:
    st.markdown("### 📊 System Info")
    
    # Feature Status
    st.markdown("#### 🔧 Available Features")
    features = {
        "Voice Recognition": "✅ Active",
        "Text-to-Speech": "✅ Active", 
        "Gemini AI": "✅ Connected",
        "Spotify": "⚠️ Web Only",
        "GIF Display": "✅ Ready",
        "Gesture Recognition": "📁 File Based",
        "Multi-Language Translator": "🌍 Tamil, Telugu, Hindi, English"
    }
    
    for feature, status in features.items():
        st.text(f"{status} {feature}")
    
    # Quick Stats
    st.markdown("#### 📈 Session Stats")
    st.metric("Commands Processed", len(st.session_state.conversation_log))
    st.metric("Current Session", f"{datetime.now().strftime('%H:%M:%S')}")
    
    # System Actions
    st.markdown("#### ⚙️ System")
    if st.button("🗑️ Clear Conversation", key="clear_log"):
        st.session_state.conversation_log = []
        st.rerun()
    
    if st.button("📝 Export Log", key="export_log"):
        export_conversation_log()
    
    if st.button("🔄 Refresh", key="refresh"):
        st.rerun()

# Auto-refresh for real-time updates
if st.session_state.is_listening:
    time.sleep(1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🤖 <strong>Zara Voice Assistant</strong> | Built with Streamlit | 
    Features: Voice Recognition, AI Chat, Music, Translation, Gestures & GIFs
</div>
""", unsafe_allow_html=True)
