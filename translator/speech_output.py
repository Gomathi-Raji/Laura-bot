import os
import time
import pygame
from gtts import gTTS

def speak_text(text, lang='hi'):
    tts = gTTS(text=text, lang=lang)
    file_path = os.path.join("assets", "speak.mp3")
    tts.save(file_path)

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.5)

    pygame.mixer.quit()
    os.remove(file_path)
