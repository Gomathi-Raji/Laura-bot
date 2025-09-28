import time
from pyfirmata import Arduino


board = Arduino('COM3')

servo_pin = 9  

board.digital[servo_pin].mode = 4  

def move_servo(angle):
    board.digital[servo_pin].write(angle)  
    time.sleep(0.5)  


move_servo(0)     
move_servo(90)    
move_servo(180)   
move_servo(90)    

board.exit()
