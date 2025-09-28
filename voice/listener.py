import speech_recognition as sr

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language='ta-IN')  # or 'ta-IN' for Tamil
        print(f"🗣️ You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("⚠️ Could not understand the audio.")
        return ""
    except sr.RequestError:
        print("⚠️ Speech Recognition service error.")
        return ""
