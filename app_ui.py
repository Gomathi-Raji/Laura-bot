import streamlit as st
import os
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
from ai.gemini_ai import get_response
from tasks.general_tasks import execute_command
from translator.speech_input import recognize_speech
from translator.translator_engine import translate_tamil_to_hindi
from translator.speech_output import speak_text

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
    
    st.markdown(f"""
    <div class="status-card {status_color.get(st.session_state.system_status, 'status-ready')}">
        <strong>Status:</strong> {st.session_state.system_status}<br>
        <strong>Mode:</strong> {st.session_state.current_mode}
    </div>
    """, unsafe_allow_html=True)
    
    # Voice Control
    st.markdown("#### 🎤 Voice Control")
    if st.button("🎙️ Start Listening", key="start_listening", help="Start voice recognition"):
        start_voice_listening()
    
    if st.button("🛑 Stop Listening", key="stop_listening", help="Stop voice recognition"):
        stop_voice_listening()
    
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
                    st.markdown(f"""
                    <div class="conversation-bubble assistant-bubble">
                        <small>{timestamp}</small><br>
                        <strong>Zara:</strong> {message}
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
