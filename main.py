import os
import subprocess
from datetime import datetime
from voice.speaker import speak
from voice.listener import listen
from ai.gemini_ai import get_response
from tasks.general_tasks import execute_command

# --- Smart Hardware Manager ---
from smart_hardware_manager import (
    get_hardware_manager, 
    smart_listen, 
    smart_speak, 
    smart_visual_feedback,
    smart_gesture_recognition,
    initialize_smart_hardware
)

# --- Tamil to Hindi Translator Imports ---
from translator.speech_input import recognize_speech
from translator.translator_engine import translate_tamil_to_hindi
from translator.speech_output import speak_text

# --- Language Learning Mode Imports ---
from translator.language_learning_mode import language_learner

# --- Debate Mode Imports ---
from ai.debate_mode import debate_mode

# --- GIF Display Imports ---
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

# --- Spotify Integration Imports ---
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI


# --- Logging Function ---
def log_conversation(role, message):
    log_path = os.path.join(os.getcwd(), "conversation_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {role}: {message}\n")


# --- GIF Display Configuration ---
speech_to_gif = {
    "hello": "hello.gif",
    "thank you": "thanks.gif",
    "yes": "yes.gif",
    "no": "no.gif"
}


def listen_and_show_gif():
    """Listen for speech and display corresponding GIF"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Listening for GIF trigger words...")
        speak("GIF முறையில் கேட்கிறேன்...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"🗣️ You said: {command}")
        log_conversation("User", command)

        for word in speech_to_gif:
            if word in command:
                gif_path = f"zara_assets/gif_output/{speech_to_gif[word]}"
                show_gif(gif_path)
                break
        else:
            print("❌ No matching GIF found for command")
            speak("அந்த வார்த்தைக்கு GIF கிடைக்கவில்லை.")
    except Exception as e:
        print(f"❌ Could not understand audio: {e}")
        speak("உங்கள் பேச்சை புரிந்துகொள்ள முடியவில்லை.")


def show_gif(gif_path):
    """Display animated GIF in a window"""
    if not os.path.exists(gif_path):
        print(f"❌ GIF file not found: {gif_path}")
        speak("GIF கோப்பு காணவில்லை.")
        return

    try:
        root = tk.Tk()
        root.title("Zara GIF Output")
        root.geometry("400x400")

        gif = Image.open(gif_path)
        frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA')) for frame in ImageSequence.Iterator(gif)]

        label = tk.Label(root)
        label.pack(expand=True)

        def update(index):
            frame = frames[index]
            index = (index + 1) % len(frames)
            label.configure(image=frame)
            root.after(100, update, index)

        root.after(0, update, 0)

        # Auto close after 5 seconds
        root.after(5000, root.destroy)
        root.mainloop()

    except Exception as e:
        print(f"❌ Error displaying GIF: {e}")
        speak("GIF காட்ட முடியவில்லை.")


# --- Spotify Integration Configuration ---
SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state playlist-modify-public"


def clear_spotify_cache():
    """Clear Spotify authentication cache"""
    cache_files = [".cache", ".cache-*"]
    for pattern in cache_files:
        import glob
        for cache_file in glob.glob(pattern):
            try:
                os.remove(cache_file)
                print(f"🗑️ Removed cache file: {cache_file}")
            except Exception as e:
                print(f"❌ Could not remove {cache_file}: {e}")


def initialize_spotify():
    """Initialize Spotify client with authentication"""
    try:
        # Clear any existing cache file
        cache_path = ".cache"
        if os.path.exists(cache_path):
            os.remove(cache_path)
            print("🗑️ Cleared Spotify cache")

        sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SPOTIFY_SCOPE,
            cache_path=cache_path
        )

        spotify = spotipy.Spotify(auth_manager=sp_oauth)
        return spotify
    except Exception as e:
        print(f"❌ Spotify authentication failed: {e}")
        speak("Spotify இணைப்பு தோல்வியடைந்தது.")
        return None


def search_and_play_song_no_auth(song_query):
    """No authentication version - just open Spotify search"""
    try:
        # Direct Spotify web search without API
        search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        webbrowser.open(search_url)

        success_msg = f"{song_query} Spotify இல் தேடப்பட்டது!"
        print(f"🌐 {success_msg}")
        speak(f"{song_query} Spotify இல் தேடுகிறேன்.")
        log_conversation("Assistant", f"Searched Spotify for: {song_query}")
        return True

    except Exception as e:
        error_msg = f"பிழை: {e}"
        print(f"❌ {error_msg}")
        speak("Spotify தேடலில் பிழை.")
        return False


def search_and_play_song_simple(song_query):
    """Simple version - search and open in web browser"""
    try:
        spotify = initialize_spotify()
        if not spotify:
            # Fallback: search on web without authentication
            search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
            webbrowser.open(search_url)
            fallback_msg = f"{song_query} வெப் பிளேயரில் தேடுகிறேன்."
            print(f"🌐 {fallback_msg}")
            speak(fallback_msg)
            return True

        print(f"🔍 Searching for: {song_query}")
        speak(f"{song_query} தேடுகிறேன்...")

        # Search for the song
        results = spotify.search(q=song_query, type='track', limit=1)

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']

            print(f"🎵 Found: {track_name} by {artist_name}")
            speak(f"{track_name} கண்டுபிடித்தேன். வெப் பிளேயரில் திறக்கிறேன்...")
            log_conversation("Assistant", f"Opening: {track_name} by {artist_name}")

            # Always open in web browser (simpler approach)
            spotify_url = f"https://open.spotify.com/track/{track['id']}"
            webbrowser.open(spotify_url)

            success_msg = f"{track_name} வெப் பிளேயரில் திறக்கப்பட்டது!"
            print(f"✅ {success_msg}")
            speak(success_msg)
            return True
        else:
            not_found_msg = f"{song_query} பாடல் கண்டுபிடிக்க முடியவில்லை."
            print(f"❌ {not_found_msg}")
            speak(not_found_msg)
            return False

    except Exception as e:
        # Fallback: direct web search
        search_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        webbrowser.open(search_url)
        fallback_msg = f"{song_query} வெப் பிளேயரில் தேடுகிறேன்."
        print(f"🌐 {fallback_msg}")
        speak(fallback_msg)
        return True


def search_and_play_song(song_query):
    """Search for a song on Spotify and play it"""
    try:
        spotify = initialize_spotify()
        if not spotify:
            return False

        print(f"🔍 Searching for: {song_query}")
        speak(f"{song_query} தேடுகிறேன்...")

        # Search for the song
        results = spotify.search(q=song_query, type='track', limit=1)

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            track_uri = track['uri']

            print(f"🎵 Found: {track_name} by {artist_name}")
            speak(f"{track_name} கண்டுபிடித்தேன். இசைக்கிறேன்...")
            log_conversation("Assistant", f"Playing: {track_name} by {artist_name}")

            # Get available devices
            devices = spotify.devices()
            if devices['devices']:
                # Play the song on the first available device
                device_id = devices['devices'][0]['id']
                spotify.start_playback(device_id=device_id, uris=[track_uri])

                success_msg = f"{track_name} இசைக்கப்படுகிறது!"
                print(f"✅ {success_msg}")
                speak(success_msg)
                return True
            else:
                # No active device found, open Spotify web player
                spotify_url = f"https://open.spotify.com/track/{track['id']}"
                webbrowser.open(spotify_url)

                fallback_msg = "Spotify சாதனம் இல்லை. வெப் பிளேயரில் திறக்கிறேன்."
                print(f"⚠️ {fallback_msg}")
                speak(fallback_msg)
                return True
        else:
            not_found_msg = f"{song_query} பாடல் கண்டுபிடிக்க முடியவில்லை."
            print(f"❌ {not_found_msg}")
            speak(not_found_msg)
            return False

    except Exception as e:
        error_msg = f"Spotify பிழை: {e}"
        print(f"❌ {error_msg}")
        speak("Spotify இல் பிழை ஏற்பட்டது.")
        return False


def listen_for_song_request():
    """Listen for song name and search/play it"""
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        speak("எந்த பாடலை கேட்க விரும்புகிறீர்கள்?")
        print("🎤 Listening for song request...")

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=10)

        song_query = recognizer.recognize_google(audio)
        print(f"🎵 Song request: {song_query}")
        log_conversation("User", f"Song request: {song_query}")

        return search_and_play_song_no_auth(song_query)  # Use no-auth version

    except sr.WaitTimeoutError:
        timeout_msg = "நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்."
        print(f"⏰ {timeout_msg}")
        speak(timeout_msg)
        return False
    except Exception as e:
        error_msg = f"பாடல் கோரிக்கை புரிந்துகொள்ள முடியவில்லை: {e}"
        print(f"❌ {error_msg}")
        speak("பாடல் கோரிக்கை புரிந்துகொள்ள முடியவில்லை.")
        return False


# Function to open gesture recognition window
def open_gesture_window():
    try:
        gesture_script_path = os.path.join(os.getcwd(), "gesture", "gesture.py")
        if os.path.exists(gesture_script_path):
            subprocess.Popen(["python", gesture_script_path])
            speak("கை சைகை விண்டோ திறக்கப்படுகிறது...")
            log_conversation("Assistant", "கை சைகை விண்டோ திறக்கப்படுகிறது...")
        else:
            speak("கை சைகை கோப்பு காணவில்லை.")
            log_conversation("Assistant", "கை சைகை கோப்பு காணவில்லை.")
            print(f"[ERROR] Gesture file not found: {gesture_script_path}")
    except Exception as e:
        speak("கை சைகை முறை செயல்படவில்லை.")
        log_conversation("Assistant", "கை சைகை முறை செயல்படவில்லை.")
        print(f"[ERROR] Failed to open gesture window: {e}")


# Multi-language translation loop with language selection
def translation_loop():
    # Language selection
    speak(
        "மொழிபெயர்ப்பு தேர்வு: தமிழ் to ஹிந்தி, தமிழ் to இங்கிலீஷ், தெலுங்கு to ஹிந்தி, தெலுங்கு to இங்கிலீஷ், ஹிந்தி to இங்கிலீஷ், அல்லது இங்கிலீஷ் to ஹிந்தி எதை விரும்புகிறீர்கள்?")
    print("🌍 Select translation language pair:")
    print("1. Tamil ➡️ Hindi")
    print("2. Tamil ➡️ English")
    print("3. Telugu ➡️ Hindi")
    print("4. Telugu ➡️ English")
    print("5. Hindi ➡️ English")
    print("6. English ➡️ Hindi")

    while True:
        try:
            selection = recognize_speech().lower()
            log_conversation("User", f"Language selection: {selection}")

            # Parse language selection
            if any(word in selection for word in ["tamil hindi", "tamil to hindi", "one", "1", "தமிழ் ஹிந்தி"]):
                source_lang = "tamil"
                target_lang = "hindi"
                break
            elif any(
                    word in selection for word in ["tamil english", "tamil to english", "two", "2", "தமிழ் இங்கிலீஷ்"]):
                source_lang = "tamil"
                target_lang = "english"
                break
            elif any(
                    word in selection for word in ["telugu hindi", "telugu to hindi", "three", "3", "தெலுங்கு ஹிந்தி"]):
                source_lang = "telugu"
                target_lang = "hindi"
                break
            elif any(word in selection for word in
                     ["telugu english", "telugu to english", "four", "4", "தெலுங்கு இங்கிலீஷ்"]):
                source_lang = "telugu"
                target_lang = "english"
                break
            elif any(word in selection for word in
                     ["hindi english", "hindi to english", "five", "5", "ஹிந்தி இங்கிலீஷ்"]):
                source_lang = "hindi"
                target_lang = "english"
                break
            elif any(word in selection for word in
                     ["english hindi", "english to hindi", "six", "6", "இங்கிலீஷ் ஹிந்தி"]):
                source_lang = "english"
                target_lang = "hindi"
                break
            else:
                speak("தெளிவான தேர்வு சொல்லுங்கள். எண்ணையும் சொல்லலாம்.")
                print("❌ Invalid selection. Please choose 1-6 or say the language pair clearly.")
                continue

        except Exception as e:
            speak("தேர்வு புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லுங்கள்.")
            print(f"❌ Could not understand selection: {e}")
            continue

    # Confirm selection
    selection_msg = f"{source_lang.title()} ➡️ {target_lang.title()} மொழிபெயர்ப்பு தேர்ந்தெடுக்கப்பட்டது."
    speak(selection_msg)
    log_conversation("Assistant", selection_msg)
    print(f"✅ Selected: {source_lang.title()} ➡️ {target_lang.title()}")

    # Start translation loop
    speak(
        f"{source_lang.title()} மொழியில் பேசுங்கள். {target_lang.title()} மொழியில் மொழிபெயர்க்கப்படுகிறது. நிறுத்த 'stop' என்று சொல்லுங்கள்.")
    log_conversation("Assistant", f"{source_lang.title()} ➡️ {target_lang.title()} translator started")
    print(
        f"🟢 {source_lang.title()} ➡️ {target_lang.title()} translator running. Say something in {source_lang.title()}.")

    while True:
        input_text = recognize_speech()
        log_conversation("User", input_text)

        if input_text.lower() in ["stop", "exit", "niruthu", "நிறுத்து", "நிற்கவும்", "வெளியேறு", "వెలుయే", "रुको",
                                  "बंद करो"]:
            speak("மொழிபெயர்ப்பு நிறுத்தப்பட்டது.")
            log_conversation("Assistant", "மொழிபெயர்ப்பு நிறுத்தப்பட்டது.")
            print("🛑 Exiting translator.")
            break

        if input_text.strip() == "":
            continue

        print(f"🗣️ {source_lang.title()}: {input_text}")

        # Use existing translation function or extend for other languages
        if source_lang == "tamil" and target_lang == "hindi":
            translated_output = translate_tamil_to_hindi(input_text)
        else:
            # For other language pairs, use a generic translation function
            translated_output = translate_text(input_text, source_lang, target_lang)

        print(f"📝 {target_lang.title()}: {translated_output}")
        log_conversation("Assistant", translated_output)
        speak_text(translated_output)


def translate_text(text, source_lang, target_lang):
    """Generic translation function for multiple language pairs"""
    try:
        # Import translation library (you can use Google Translate API or similar)
        from googletrans import Translator
        translator = Translator()

        # Language code mapping
        lang_codes = {
            "tamil": "ta",
            "telugu": "te",
            "hindi": "hi",
            "english": "en"
        }

        source_code = lang_codes.get(source_lang, "ta")
        target_code = lang_codes.get(target_lang, "hi")

        result = translator.translate(text, src=source_code, dest=target_code)
        return result.text

    except Exception as e:
        print(f"❌ Translation error: {e}")
        # Fallback to existing function if available
        if source_lang == "tamil" and target_lang == "hindi":
            return translate_tamil_to_hindi(text)
        else:
            return f"Translation error for {source_lang} to {target_lang}: {text}"


def language_learning_mode():
    """Interactive Language Learning Mode with Tamil, English, and Hindi"""
    print("\n🎓 === LANGUAGE LEARNING MODE ACTIVATED ===")
    speak("லாங்குவேஜ் லேர்னிங் மோட் ஆக்டிவேட் ஆயிருச்சு!")
    
    # Show available language combinations
    speak("மூன்று மொழிகள்: தமிழ், இங்கிலீஷ், ஹிந்தி. எந்த மொழியிலிருந்து எந்த மொழிக்கு கற்க வேண்டும்?")
    print("🌍 Available Language Learning Combinations:")
    print("1️⃣ Tamil ➡️ English (தமிழ் ➡️ இங்கிலீஷ்)")
    print("2️⃣ Tamil ➡️ Hindi (தமிழ் ➡️ ஹிந்தி)")
    print("3️⃣ English ➡️ Tamil (English ➡️ தமிழ்)")
    print("4️⃣ English ➡️ Hindi (English ➡️ हिंदी)")
    print("5️⃣ Hindi ➡️ Tamil (हिंदी ➡️ தமிழ்)")
    print("6️⃣ Hindi ➡️ English (हिंदी ➡️ English)")
    print("7️⃣ Practice Mode (பயிற்சி மோட்)")
    print("8️⃣ Quiz Mode (வினாடி வினா)")
    print("9️⃣ Learning Stats (கற்றல் புள்ளிவிவரம்)")
    
    # Get user selection
    source_lang = ""
    target_lang = ""
    mode_type = "translation"
    
    while True:
        try:
            speak("உங்கள் தேர்வை சொல்லுங்கள்.")
            selection = recognize_speech().lower()
            log_conversation("User", selection)
            
            if any(word in selection for word in ["tamil english", "tamil to english", "one", "1", "தமிழ் இங்கிலீஷ்"]):
                source_lang, target_lang = "tamil", "english"
                break
            elif any(word in selection for word in ["tamil hindi", "tamil to hindi", "two", "2", "தமிழ் ஹிந்தி"]):
                source_lang, target_lang = "tamil", "hindi"
                break
            elif any(word in selection for word in ["english tamil", "english to tamil", "three", "3", "இங்கிலீஷ் தமிழ்"]):
                source_lang, target_lang = "english", "tamil"
                break
            elif any(word in selection for word in ["english hindi", "english to hindi", "four", "4", "இங்கிலீஷ் ஹிந்தி"]):
                source_lang, target_lang = "english", "hindi"
                break
            elif any(word in selection for word in ["hindi tamil", "hindi to tamil", "five", "5", "ஹிந்தி தமிழ்"]):
                source_lang, target_lang = "hindi", "tamil"
                break
            elif any(word in selection for word in ["hindi english", "hindi to english", "six", "6", "ஹiந்தி இங்கிलீஷ்"]):
                source_lang, target_lang = "hindi", "english"
                break
            elif any(word in selection for word in ["practice", "seven", "7", "பயிற்சி", "practice mode"]):
                mode_type = "practice"
                break
            elif any(word in selection for word in ["quiz", "eight", "8", "வினாடி வினா", "quiz mode"]):
                mode_type = "quiz"
                break
            elif any(word in selection for word in ["stats", "nine", "9", "புள்ளிவிவரம்", "statistics"]):
                show_learning_stats()
                continue
            else:
                speak("தெளிவான தேர்வு சொல்லுங்கள். ஒன்று முதல் ஒன்பது வரை.")
                print("❌ Please choose 1-9 or say the option clearly.")
                continue
                
        except Exception as e:
            speak("தேர்வு புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லுங்கள்.")
            print(f"❌ Could not understand selection: {e}")
            continue
    
    # Execute selected mode
    if mode_type == "practice":
        start_practice_mode()
    elif mode_type == "quiz":
        start_quiz_mode()
    else:
        start_learning_translation(source_lang, target_lang)


def start_learning_translation(source_lang, target_lang):
    """Start interactive learning translation"""
    selection_msg = f"{source_lang.title()} ➡️ {target_lang.title()} கற்றல் முறை தேர்ந்தெடுக்கப்பட்டது."
    speak(selection_msg)
    log_conversation("Assistant", selection_msg)
    print(f"✅ Learning Mode: {source_lang.title()} ➡️ {target_lang.title()}")
    
    # Get practice suggestions
    language_pair = f"{source_lang}_{target_lang}"
    suggestions = language_learner.get_practice_suggestion(language_pair)
    
    if suggestions:
        speak("பயிற்சிக்கான சில பரிந்துரைகள்:")
        print("💡 Practice Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    speak(f"{source_lang.title()} மொழியில் பேசுங்கள். விரிவான கற்றல் தகவல்களுடன் {target_lang.title()} மொழியில் மொழிபெயர்க்கப்படும்.")
    print(f"🎓 Learning Translation Mode Active. Say something in {source_lang.title()}.")
    
    while True:
        input_text = recognize_speech()
        log_conversation("User", input_text)
        
        if input_text.lower() in ["stop", "exit", "niruthu", "நிறுத்து", "quit", "learning complete"]:
            speak("கற்றல் முறை நிறுத்தப்பட்டது. நன்றி!")
            log_conversation("Assistant", "Language learning mode stopped.")
            print("🛑 Exiting language learning mode.")
            show_session_summary()
            break
            
        if input_text.strip() == "":
            continue
            
        print(f"🗣️ {source_lang.title()}: {input_text}")
        
        # Get enhanced translation with learning features
        result = language_learner.translate_with_learning(input_text, source_lang, target_lang)
        
        translation = result.get('translation', 'Translation error')
        pronunciation = result.get('pronunciation', '')
        grammar_note = result.get('grammar_note', '')
        cultural_context = result.get('cultural_context', '')
        
        print(f"📝 {target_lang.title()}: {translation}")
        speak_text(translation)
        
        # Provide additional learning information
        if pronunciation:
            print(f"🔊 Pronunciation: {pronunciation}")
            
        if grammar_note:
            print(f"📚 Grammar: {grammar_note}")
            speak(f"கிராமர் குறிப்பு: {grammar_note}")
            
        if cultural_context:
            print(f"🌍 Cultural Context: {cultural_context}")
            
        log_conversation("Assistant", f"Translation: {translation}")


def start_practice_mode():
    """Start practice mode with random phrases"""
    speak("பயிற்சி முறை தொடங்குகிறது!")
    print("🏋️ === PRACTICE MODE ===")
    
    # Choose a random language combination
    import random
    combinations = [
        ('tamil', 'english'), ('tamil', 'hindi'), ('english', 'tamil'),
        ('english', 'hindi'), ('hindi', 'tamil'), ('hindi', 'english')
    ]
    
    source_lang, target_lang = random.choice(combinations)
    speak(f"{source_lang.title()} இலிருந்து {target_lang.title()} பயிற்சி.")
    
    # Get practice phrases
    language_pair = f"{source_lang}_{target_lang}"
    suggestions = language_learner.get_practice_suggestion(language_pair)
    
    if not suggestions:
        speak("பயிற்சிக்கான சொற்கள் கிடைக்கவில்லை. முதலில் சில வார்த்தைகளை கற்றுக்கொள்ளுங்கள்.")
        return
    
    for phrase in suggestions:
        speak(f"இதை மொழிபெயர்க்கவும்: {phrase}")
        print(f"🔄 Translate: {phrase}")
        
        user_translation = recognize_speech()
        if user_translation.lower() in ["stop", "exit", "skip"]:
            break
            
        correct_answer = language_learner.simple_translate(phrase, source_lang, target_lang)
        print(f"✅ Correct Answer: {correct_answer}")
        speak(f"சரியான பதில்: {correct_answer}")
        
        log_conversation("Practice", f"Q: {phrase} | User: {user_translation} | Correct: {correct_answer}")


def start_quiz_mode():
    """Start quiz mode"""
    speak("வினாடி வினா முறை!")
    print("🧠 === QUIZ MODE ===")
    
    # Ask for language combination
    speak("எந்த மொழி கலவைக்கு வினாடி வினா வேண்டும்?")
    
    # For now, use a default combination
    source_lang, target_lang = "tamil", "english"
    
    quiz = language_learner.generate_quiz(source_lang, target_lang)
    
    if not quiz:
        speak("வினாடி வினாவுக்கு போதுமான தகவல் இல்லை. முதலில் கொஞ்சம் கற்றுக்கொள்ளுங்கள்.")
        print("❌ Not enough learned words for quiz. Learn some words first.")
        return
    
    score = 0
    total_questions = len(quiz['questions'])
    
    speak(f"{total_questions} கேள்விகள் உள்ளன.")
    
    for i, question in enumerate(quiz['questions'], 1):
        print(f"\n❓ Question {i}/{total_questions}: {question['question']}")
        speak(f"கேள்வி {i}: {question['source_text']} இதை மொழிபெயர்க்கவும்.")
        
        user_answer = recognize_speech()
        correct_answer = question['correct_answer']
        
        if user_answer.lower().strip() == correct_answer.lower().strip():
            score += 1
            print("✅ Correct!")
            speak("சரி!")
        else:
            print(f"❌ Wrong. Correct answer: {correct_answer}")
            speak(f"தவறு. சரியான பதில்: {correct_answer}")
    
    # Show final score
    percentage = (score / total_questions) * 100
    print(f"\n🏆 Quiz Complete! Score: {score}/{total_questions} ({percentage:.1f}%)")
    speak(f"வினாடி வினா முடிந்தது! மதிப்பெண்: {score} out of {total_questions}")
    
    log_conversation("Quiz", f"Score: {score}/{total_questions}")


def show_learning_stats():
    """Show learning statistics"""
    stats = language_learner.get_learning_stats()
    
    print("\n📊 === LEARNING STATISTICS ===")
    print(f"📝 Total Translations: {stats['total_translations']}")
    print(f"🌍 Languages Practiced: {len(stats['languages_practiced'])}")
    print(f"🎯 This Session: {stats['session_count']} translations")
    
    mastery = stats['mastery_breakdown']
    print(f"📈 Mastery Levels:")
    print(f"   🟢 Beginner: {mastery['beginner']}")
    print(f"   🟡 Intermediate: {mastery['intermediate']}")
    print(f"   🔴 Advanced: {mastery['advanced']}")
    
    # Speak key statistics
    speak(f"மொத்தம் {stats['total_translations']} மொழிபெயர்ப்புகள் செய்யப்பட்டுள்ளன.")
    
    log_conversation("Stats", f"Total: {stats['total_translations']}, Session: {stats['session_count']}")


def show_session_summary():
    """Show summary of current learning session"""
    session = language_learner.current_session
    
    if session['translations']:
        print(f"\n📋 Session Summary: {len(session['translations'])} new translations learned")
        speak(f"இந்த அமர்வில் {len(session['translations'])} புதிய மொழிபெயர்ப்புகள் கற்றுக்கொண்டீர்கள்.")
    else:
        speak("இந்த அமர்வில் புதிய மொழிபெயர்ப்புகள் இல்லை.")


def debate_mode_session():
    """Interactive Debate Mode with AI"""
    print("\n🎯 === DEBATE MODE ACTIVATED ===")
    speak("டிபேட் மோட் ஆக்டிவேட் ஆயிருச்சு! Let's have an engaging discussion!")
    
    # Show debate options
    speak("நீங்கள் என்ன விஷயத்தை பற்றி விவாதிக்க விரும்புகிறீர்கள்?")
    print("🗣️ Debate Mode Options:")
    print("1️⃣ Choose a topic from suggestions")
    print("2️⃣ Suggest your own topic")
    print("3️⃣ Random topic surprise")
    print("4️⃣ View debate statistics")
    print("5️⃣ Exit debate mode")
    
    while True:
        try:
            speak("உங்கள் தேர்வை சொல்லுங்கள்.")
            selection = recognize_speech().lower()
            log_conversation("User", selection)
            
            if any(word in selection for word in ["suggestions", "choose topic", "one", "1", "பரிந்துரைகள்"]):
                start_topic_selection()
                break
            elif any(word in selection for word in ["own topic", "suggest", "two", "2", "என் விஷயம்"]):
                start_custom_topic()
                break
            elif any(word in selection for word in ["random", "surprise", "three", "3", "சீரற்ற"]):
                start_random_debate()
                break
            elif any(word in selection for word in ["statistics", "stats", "four", "4", "புள்ளிவிவரம்"]):
                show_debate_statistics()
                continue
            elif any(word in selection for word in ["exit", "quit", "five", "5", "வெளியேறு"]):
                speak("டிபேட் மோட் நிறுத்தப்பட்டது. நன்றி!")
                break
            else:
                speak("தெளிவான தேர்வு சொல்லுங்கள். ஒன்று முதல் ஐந்து வரை.")
                print("❌ Please choose 1-5 or say the option clearly.")
                continue
                
        except Exception as e:
            speak("தேர்வு புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லுங்கள்.")
            print(f"❌ Could not understand selection: {e}")
            continue


def start_topic_selection():
    """Start debate with topic suggestions"""
    suggestions = debate_mode.get_debate_suggestions()
    
    print("\n📝 Suggested Debate Topics:")
    speak("இங்கே சில விவாத தலைப்புகள்:")
    
    for i, topic in enumerate(suggestions['suggested_topics'], 1):
        print(f"   {i}. {topic}")
    
    speak("எந்த தலைப்பை தேர்ந்தெடுக்க விரும்புகிறீர்கள்?")
    print("🎯 Say the number (1-5) or describe the topic you want to debate.")
    
    while True:
        try:
            choice = recognize_speech().lower()
            log_conversation("User", choice)
            
            # Check for numbers
            topic_selected = None
            for i, topic in enumerate(suggestions['suggested_topics'], 1):
                if str(i) in choice or f"number {i}" in choice:
                    topic_selected = topic
                    break
            
            if topic_selected:
                result = debate_mode.start_debate(topic_selected)
                start_debate_session(result)
                break
            else:
                speak("தெளிவான எண் சொல்லுங்கள் அல்லது தலைப்பை விவரிக்கவும்.")
                continue
                
        except Exception as e:
            speak("புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லுங்கள்.")
            continue


def start_custom_topic():
    """Start debate with user's custom topic"""
    speak("உங்கள் விவாத தலைப்பை சொல்லுங்கள்.")
    print("🎤 What would you like to debate about? State your topic:")
    
    try:
        custom_topic = recognize_speech()
        log_conversation("User", f"Custom topic: {custom_topic}")
        
        if custom_topic.strip():
            result = debate_mode.start_debate(custom_topic)
            speak(f"சிறந்த தலைப்பு! {custom_topic} பற்றி விவாதிக்கலாம்.")
            start_debate_session(result)
        else:
            speak("தலைப்பு கேட்கவில்லை. மீண்டும் முயற்சிக்கவும்.")
            
    except Exception as e:
        speak("தலைப்பு புரிந்துகொள்ள முடியவில்லை.")
        print(f"❌ Could not understand topic: {e}")


def start_random_debate():
    """Start debate with random topic"""
    suggestions = debate_mode.get_debate_suggestions()
    random_topic = suggestions['random_topic']
    
    speak(f"சீரற்ற தலைப்பு: {random_topic}")
    print(f"🎲 Random Topic: {random_topic}")
    
    result = debate_mode.start_debate(random_topic)
    start_debate_session(result)


def start_debate_session(debate_setup):
    """Main debate session loop"""
    print(f"\n🎯 Debate Topic: {debate_setup['topic']}")
    print("📋 Choose your position:")
    
    positions = debate_setup['suggested_positions']
    print(f"1️⃣ PRO: {positions['pro']}")
    print(f"2️⃣ CON: {positions['con']}")
    
    speak("நீங்கள் எந்த நிலைப்பாட்டை எடுக்க விரும்புகிறீர்கள்? வேண்டும் அல்லது வேண்டாம்?")
    
    # Get user position
    while True:
        try:
            position_choice = recognize_speech().lower()
            log_conversation("User", position_choice)
            
            user_position = ""
            if any(word in position_choice for word in ["pro", "support", "agree", "yes", "one", "1", "வேண்டும்"]):
                user_position = positions['pro']
            elif any(word in position_choice for word in ["con", "against", "disagree", "no", "two", "2", "வேண்டாம்"]):
                user_position = positions['con']
            else:
                speak("PRO அல்லது CON தேர்ந்தெடுக்கவும். ஒன்று அல்லது இரண்டு சொல்லுங்கள்.")
                continue
            
            # Set positions and start debate
            setup_result = debate_mode.set_user_position(user_position)
            
            print(f"✅ Your Position: {setup_result['user_position']}")
            print(f"🤖 AI Position: {setup_result['ai_position']}")
            speak("நல்லது! நான் எதிர் நிலைப்பாட்டை எடுப்பேன். உங்கள் முதல் வாதத்தை முன்வையுங்கள்.")
            
            # Start argument exchange
            conduct_debate_rounds()
            break
            
        except Exception as e:
            speak("நிலைப்பாட்டை புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லுங்கள்.")
            continue


def conduct_debate_rounds():
    """Conduct the main debate argument exchange"""
    round_count = 0
    max_rounds = 5
    
    speak(f"விவாதம் தொடங்குகிறது! மொத்தம் {max_rounds} சுற்றுகள். உங்கள் வாதத்தை ஆரம்பிக்கவும்.")
    
    while round_count < max_rounds:
        print(f"\n🔄 Round {round_count + 1} of {max_rounds}")
        print("🎤 Present your argument:")
        speak("உங்கள் வாதத்தை முன்வையுங்கள்.")
        
        try:
            user_argument = recognize_speech()
            if not user_argument.strip():
                speak("வாதம் கேட்கவில்லை. மீண்டும் முயற்சிக்கவும்.")
                continue
            
            log_conversation("User Argument", user_argument)
            print(f"👤 Your Argument: {user_argument}")
            
            # Get AI response
            result = debate_mode.process_user_argument(user_argument)
            
            print(f"\n🤖 AI Counter-Argument: {result['ai_argument']}")
            if result.get('ai_reasoning'):
                print(f"📊 AI Reasoning: {result['ai_reasoning']}")
            
            speak(f"என் மறுப்பு: {result['ai_argument']}")
            log_conversation("AI Counter-Argument", result['ai_argument'])
            
            # Show round evaluation
            evaluation = result['round_evaluation']
            print(f"\n📈 Round {result['round_number']} Evaluation:")
            print(f"🏆 Round Winner: {evaluation['round_winner']}")
            print(f"💬 Feedback: {evaluation['feedback']}")
            print(f"⭐ Strongest Point: {evaluation['strongest_point']}")
            
            # Update round count
            round_count = result['round_number']
            
            if not result['continue_debate']:
                break
                
            # Ask if user wants to continue
            speak("அடுத்த சுற்றுக்கு தயாரா? Continue என்று சொல்லுங்கள்.")
            continue_response = recognize_speech().lower()
            
            if any(word in continue_response for word in ["stop", "end", "finish", "நிறுத்து", "முடி"]):
                break
                
        except Exception as e:
            speak("வாதத்தை புரிந்துகொள்ள முடியவில்லை. மீண்டும் முயற்சிக்கவும்.")
            print(f"❌ Error in debate round: {e}")
            continue
    
    # End debate and show final results
    final_result = debate_mode.end_debate()
    show_debate_conclusion(final_result)


def show_debate_conclusion(final_result):
    """Show final debate results and evaluation"""
    print("\n🏁 === DEBATE CONCLUDED ===")
    speak("விவாதம் முடிந்தது! முடிவுகளை காண்போம்.")
    
    print(f"🏆 Overall Winner: {final_result['overall_winner'].upper()}")
    print(f"📊 Final Score - You: {final_result['final_score']['user']}, AI: {final_result['final_score']['ai']}")
    
    speak(f"ஒட்டுமொத்த வெற்றியாளர்: {final_result['overall_winner']}")
    
    print(f"\n✅ Your Strengths: {', '.join(final_result['user_strengths'])}")
    print(f"📈 Areas for Improvement: {', '.join(final_result['user_improvements'])}")
    print(f"🎯 Key Insights: {', '.join(final_result['key_insights'])}")
    print(f"📚 Learning Outcomes: {', '.join(final_result['learning_outcomes'])}")
    print(f"\n📝 Summary: {final_result['summary']}")
    
    speak("சிறந்த விவாதம்! நீங்கள் நல்லா பங்கேற்றீர்கள்.")
    log_conversation("Debate Conclusion", f"Winner: {final_result['overall_winner']}, Quality: {final_result['debate_quality']}")


def show_debate_statistics():
    """Show debate statistics and history"""
    stats = debate_mode.get_debate_stats()
    
    print("\n📊 === DEBATE STATISTICS ===")
    print(f"🎯 Total Debates: {stats['total_debates']}")
    print(f"🏆 Your Wins: {stats['user_wins']} ({stats['user_win_rate']}%)")
    print(f"🤖 AI Wins: {stats['ai_wins']} ({stats['ai_win_rate']}%)")
    print(f"🤝 Draws: {stats['draws']} ({stats['draw_rate']}%)")
    
    if stats['recent_topics']:
        print("\n📝 Recent Debate Topics:")
        for i, topic_info in enumerate(stats['recent_topics'], 1):
            print(f"   {i}. {topic_info['topic']} (Winner: {topic_info['winner']})")
    
    speak(f"மொத்தம் {stats['total_debates']} விவாதங்கள் செய்துள்ளீர்கள். உங்கள் வெற்றி விகிதம் {stats['user_win_rate']} சதவீதம்.")


# Process user commands
def process_command(command):
    if not command:
        return

    print(f"[USER COMMAND]: {command}")
    log_conversation("User", command)

    # If gesture command
    if any(kw in command.lower() for kw in
           ["gesture", "கை சைகை", "open gesture", "start gesture", "ஆக்டிவேட் ஜெஸ்சர்", "activate gesture"]):
        open_gesture_window()
        return

    # If GIF display command
    if any(kw in command.lower() for kw in ["gif", "show gif", "display gif", "GIF காட்டு", "gif காட்டு"]):
        listen_and_show_gif()
        return

    # If Spotify/music command
    if any(kw in command.lower() for kw in
           ["play song", "play music", "spotify", "பாடல் இசை", "இசை இசை", "song play", "music play", "ப்ளே மியூசிக்",
            "மியூசிக் ப்ளே"]):
        listen_for_song_request()
        return

    # If direct song search (contains "play" + song name)
    if "play" in command.lower() and len(command.split()) > 1:
        # Extract song name after "play"
        parts = command.lower().split("play", 1)
        if len(parts) > 1:
            song_name = parts[1].strip()
            if song_name:
                search_and_play_song_no_auth(song_name)  # Use no-auth version
                return

    # If user wants debate mode
    if any(kw in command.lower() for kw in ["debate mode", "debate", "விவாதம்", "டிபேட் மோட்", "discussion", "argue", "விவாதிக்க", "டிபேட்"]):
        debate_mode_session()
        return
    
    # If user wants language learning mode
    if any(kw in command.lower() for kw in ["language mode", "language learning", "லாং்குवেজ் மோড്", "কর্তল முறை", "learn language", "language teach", "மொழি কர্ক"]):
        language_learning_mode()
        return
    
    # If user wants translator mode (basic)
    if any(kw in command.lower() for kw in ["translator", "translate", "মোژিপেয়র్প্প্", "tamil to hindi", "আক্টিভেত্ ট্রান্স্লেট্ মোড়্", "ট্রান্স্লেত্"]):
        translation_loop()
        return

    # If general task command
    if execute_command(command):
        log_conversation("Assistant", "Executed general task command.")
        return

    # If none of the above, use Gemini AI to respond with smart hardware
    smart_visual_feedback('thinking')
    response = get_response(command)
    log_conversation("Assistant", response)
    smart_speak_response(response)


# Smart hardware listening with fallback
def smart_listen_command():
    """Listen for commands using smart hardware manager with fallbacks"""
    try:
        hardware_manager = get_hardware_manager()
        
        # Use smart listening with fallback
        result = smart_listen(timeout=10, simulation_input="hello laura")
        
        if result['success']:
            print(f"🎤 Input via {result['method_used']}: {result['data']}")
            return result['data']
        else:
            print(f"❌ Listening failed: {result['message']}")
            return ""
            
    except Exception as e:
        print(f"⚠️ Smart listen error: {e}")
        # Fallback to original listening
        try:
            return listen()
        except:
            return ""

# Smart speaking with hardware fallback
def smart_speak_response(message):
    """Speak response using smart hardware manager with fallbacks"""
    try:
        result = smart_speak(message)
        print(f"🔊 Output via {result['method_used']}: {result['message']}")
        
        # Also provide visual feedback
        if "correct" in message.lower() or "good" in message.lower():
            smart_visual_feedback('celebrate')
        elif "thinking" in message.lower() or "processing" in message.lower():
            smart_visual_feedback('thinking')
        else:
            smart_visual_feedback('listening')
            
    except Exception as e:
        print(f"⚠️ Smart speak error: {e}")
        # Fallback to original speaking
        try:
            speak(message)
        except:
            print(f"[FALLBACK TEXT]: {message}")

# Hardware-aware command processing
def process_command_with_hardware(command):
    """Process commands with hardware awareness"""
    if not command:
        return

    print(f"[USER COMMAND]: {command}")
    log_conversation("User", command)

    # Hardware testing commands
    if any(kw in command.lower() for kw in ["test hardware", "hardware test", "check hardware", "hardware status"]):
        hardware_manager = get_hardware_manager()
        hardware_manager.test_all_hardware()
        smart_speak_response("ஹார்ட்வேர் டெஸ்ட் முடிந்தது. எல்லா கம்போனெண்ட்ஸ் சரிபார்க்கப்பட்டது.")
        return

    # Hardware report command  
    if any(kw in command.lower() for kw in ["hardware report", "system status", "சிஸ்டம் ஸ்டேட்டஸ்"]):
        hardware_manager = get_hardware_manager()
        hardware_manager.generate_hardware_report()
        smart_speak_response("சிஸ்டம் ரிப்போர்ட் தயார். கன்சோலில் பார்க்கவும்.")
        return

    # Gesture recognition command
    if any(kw in command.lower() for kw in ["recognize gesture", "gesture recognition", "கை சைகை அடையாளம்"]):
        result = smart_gesture_recognition()
        if result['success']:
            gesture = result['data']
            response = f"கை சைகை கண்டுபிடிக்கப்பட்டது: {gesture}"
            smart_speak_response(response)
            smart_visual_feedback('celebrate')
        else:
            smart_speak_response("கை சைகை கண்டுபிடிக்க முடியவில்லை.")
        return

    # If gesture command (enhanced with hardware)
    if any(kw in command.lower() for kw in
           ["gesture", "கை சைகை", "open gesture", "start gesture", "ஆக்டிவேட் ஜெஸ்சர்", "activate gesture"]):
        # Try smart gesture recognition first
        result = smart_gesture_recognition()
        if result['method_used'] == 'camera':
            smart_speak_response("கேமரா வழியாக கை சைகை அடையாளம் காணப்படுகிறது.")
        else:
            # Fallback to original gesture window
            open_gesture_window()
        return

    # If GIF display command
    if any(kw in command.lower() for kw in ["gif", "show gif", "display gif", "GIF காட்டு", "gif காட்டு"]):
        listen_and_show_gif()
        return

    # If Spotify/music command
    if any(kw in command.lower() for kw in
           ["play song", "play music", "spotify", "பாடல் இசை", "இசை இசை", "song play", "music play", "ப்ளே மியூசிக்",
            "மியூசிக் ப்ளே"]):
        listen_for_song_request()
        return

    # If direct song search (contains "play" + song name)
    if "play" in command.lower() and len(command.split()) > 1:
        # Extract song name after "play"
        parts = command.lower().split("play", 1)
        if len(parts) > 1:
            song_name = parts[1].strip()
            if song_name:
                search_and_play_song_no_auth(song_name)  # Use no-auth version
                return

    # If user wants debate mode
    if any(kw in command.lower() for kw in ["debate mode", "debate", "விவாதம்", "டிபேட் மோட்", "discussion", "argue", "விவாதிக்க", "டிபேட்"]):
        smart_visual_feedback('thinking')
        debate_mode_session()
        return
    
    # If user wants language learning mode
    if any(kw in command.lower() for kw in ["language mode", "language learning", "லாங்குवेজ் மோட্", "কর্তল முறை", "learn language", "language teach", "মোজি கর্क"]):
        smart_visual_feedback('listening')
        language_learning_mode()
        return
    
    # If user wants translator mode (basic)
    if any(kw in command.lower() for kw in ["translator", "translate", "মোজিপেয়র্প্প্", "tamil to hindi", "আক্টিভেت্ ট্রান্স্লেট্ মোড়্", "ট্রান্স্লেত্"]):
        smart_visual_feedback('listening')
        translation_loop()
        return

    # If general task command
    if execute_command(command):
        log_conversation("Assistant", "Executed general task command.")
        smart_visual_feedback('celebrate')
        return

    # If none of the above, use Gemini AI to respond
    smart_visual_feedback('thinking')
    response = get_response(command)
    log_conversation("Assistant", response)
    smart_speak_response(response)

# Entry point
if __name__ == "__main__":
    print("🚀 Initializing Laura-bot with Smart Hardware Management...")
    
    # Initialize smart hardware management
    try:
        hardware_manager = initialize_smart_hardware()
        print("✅ Smart hardware management initialized")
    except Exception as e:
        print(f"⚠️ Hardware initialization error: {e}")
        print("🤖 Continuing with basic functionality...")
    
    welcome_msg = "வணக்கம்! நான் லாரா. இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
    smart_speak_response(welcome_msg)
    log_conversation("Assistant", welcome_msg)
    
    print("\n💡 Available Commands:")
    print("🎤 Voice Commands: 'debate mode', 'language learning', 'play music'")
    print("🔧 Hardware Commands: 'test hardware', 'hardware report', 'recognize gesture'")
    print("🎮 Gesture Commands: 'gesture', 'activate gesture'")
    print("🌐 Web Interface: Run 'python laura_bot_server.py' for web access")
    print("\n🎯 Say something to start...")
    
    while True:
        try:
            command = smart_listen_command()
            process_command_with_hardware(command)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            smart_speak_response("வணக்கம்! மீண்டும் வருக!")
            
            # Cleanup hardware
            try:
                hardware_manager = get_hardware_manager()
                hardware_manager.cleanup()
            except:
                pass
            break
        except Exception as e:
            print(f"⚠️ Main loop error: {e}")
            smart_speak_response("மன்னிக்கவும், ஏதோ பிரச்சனை. மீண்டும் முயற்சிக்கவும்.")
            continue