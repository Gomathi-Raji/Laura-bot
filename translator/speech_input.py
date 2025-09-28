import speech_recognition as sr

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... (say 'niruthu' to stop)")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="ta-IN")
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError:
        print("❌ Speech Recognition service unavailable.")
        return ""
