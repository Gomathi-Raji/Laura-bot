import cv2
import mediapipe as mp
hand_detect1=mp.solutions.hands
hand_detect=hand_detect1.Hands()
import pyautogui
import time

draw_utits=mp.solutions.drawing_utils
cap=cv2.VideoCapture("http://10.170.105.110:81/stream")
fingerTips=[4,8,12,16,20]
while True:
    _,frame=cap.read()
    f_h,f_w,_=frame.shape
    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    output=hand_detect.process(rgb_frame)
    hands=output.multi_hand_landmarks
    lmList=[]
    fingers=[]
    if hands:
        for hand in hands:
            draw_utits.draw_landmarks(frame,hand,hand_detect1.HAND_CONNECTIONS)
            landmarks=hand.landmark
            for id,landmark in enumerate(landmarks):
                x=int(landmark.x*f_w)
                y=int(landmark.y*f_h)
                lmList.append([id,x,y])
    if len(lmList)!=0:
        if lmList[fingerTips[0]][1]  >lmList[fingerTips[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1,5):
            if lmList[fingerTips[id]][2]<lmList[fingerTips[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        total=fingers.count(1)
        if total==5:
            pyautogui.press('space')
            time.sleep(1)
        if total==1:
            pyautogui.press('nexttrack')
            time.sleep(1)
        if total == 2:
            pyautogui.press('prevtrack')
            time.sleep(1)
        if total == 3:
            pyautogui.press('up')
            time.sleep(1)
        if total == 4:
            pyautogui.press('down')
            time.sleep(1)
        #cv2.putText(frame,f'finger_count== {total}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),5)
    cv2.imshow("frame",frame)
    cv2.waitKey(1)