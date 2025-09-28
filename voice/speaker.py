from gtts import gTTS
import pygame
import os


import time
from pyfirmata import Arduino


board = Arduino('COM7')

servo_pin = 9
servo_pin1 = 10

board.digital[servo_pin].mode = 4
board.digital[servo_pin1].mode = 4

def speak(text):
    print(f"🤖 zara (Tamil): {text}")
    tts = gTTS(text=text, lang='ta')
    tts.save("voice.mp3")

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("voice.mp3")


    pygame.mixer.music.play()



    while pygame.mixer.music.get_busy():
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

    pygame.mixer.quit()
    os.remove("voice.mp3")
