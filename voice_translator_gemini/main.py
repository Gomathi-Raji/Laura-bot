from translator.speech_input import recognize_speech
from translator.translator_engine import translate_tamil_to_hindi
from translator.speech_output import speak_text

def tamil_to_hindi_loop():
    print("🟢 Tamil ➡️ Hindi translator running. Say something in Tamil.")
    while True:
        input_text = recognize_speech()

        if input_text.lower() in ["niruthu", "stop", "exit"]:
            print("🛑 Exiting translator.")
            break

        if input_text.strip() == "":
            continue

        print(f"🗣️ Tamil: {input_text}")
        hindi_output = translate_tamil_to_hindi(input_text)
        print(f"📝 Hindi: {hindi_output}")
        speak_text(hindi_output)

if __name__ == "__main__":
    tamil_to_hindi_loop()
