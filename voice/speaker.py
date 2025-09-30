from gtts import gTTS
import pygame
import os


import time
from pyfirmata import Arduino

# Initialize Arduino connection with error handling
board = None
servo_pin = 9
servo_pin1 = 10

try:
    board = Arduino('COM7')
    board.digital[servo_pin].mode = 4
    board.digital[servo_pin1].mode = 4
    print("✅ Arduino connected successfully on COM7")
except Exception as e:
    print(f"⚠️ Arduino not available: {str(e)}")
    print("🔄 Running in simulation mode without hardware")

def speak(text):
    print(f"🤖 zara (Tamil): {text}")
    tts = gTTS(text=text, lang='ta')
    tts.save("voice.mp3")

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("voice.mp3")


    pygame.mixer.music.play()



    while pygame.mixer.music.get_busy():
        if board:  # Only control servo if Arduino is connected
            board.digital[servo_pin].write(0)
            time.sleep(0.9)
            board.digital[servo_pin1].write(0)
            time.sleep(0.9)
            board.digital[servo_pin].write(90)
            time.sleep(0.9)
            board.digital[servo_pin1].write(90)
            time.sleep(0.9)
            board.digital[servo_pin].write(120)
            time.sleep(0.9)
            board.digital[servo_pin1].write(120)
            time.sleep(0.9)
            board.digital[servo_pin].write(180)
            time.sleep(0.9)
            board.digital[servo_pin1].write(180)
            time.sleep(0.9)
        else:
            time.sleep(0.1)  # Small delay when no Arduino

    pygame.mixer.quit()
    os.remove("voice.mp3")
