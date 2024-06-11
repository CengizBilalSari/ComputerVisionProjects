import cv2
import mediapipe
import time
import numpy as np
import HandTrackingModule as htm
import math

cap= cv2.VideoCapture(0)
#####################
wCam,hCam= 1280,720
#####################
pTime=0
detector= htm.handDetector(min_detection_confidence=0.7)
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()

minVol= volRange[0]
maxVol= volRange[1]

vol=0
vol_bar=400
vol_per=0
while True:
    success,img= cap.read()
    img= detector.findHands(img)
    lm_list= detector.findPosition(img,draw=False)
    if (len(lm_list)!=0):

        x1,y1=lm_list[4][1],lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        cx,cy= (x1+x2)//2,(y1+y2)//2
        cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
        cv2.circle(img,(x2,y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length= math.hypot(x2-x1,y2-y1)

        # Hand range: 50-250
        # Volume range: -63.5-0
        vol = np.interp(length, [50,250], [minVol, maxVol])
        vol_bar= np.interp(length, [50, 250], [400,150])
        vol_per = np.interp(length, [50,250], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)
        if length<50:
            cv2.circle(img, (cx, cy), 15, (0, 255,0), cv2.FILLED)

    cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img,(50,int(vol_bar)),(85,400),(0,255,0),cv2.FILLED)
    cv2.putText(img, f'{int(vol_per)}%', (40, 450), cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 0, 0), 3)





    cTime= time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img,f'FPS:{int(fps)}',(40,70),cv2.FONT_HERSHEY_PLAIN,2,
                (255,0),3)
    cv2.imshow("Image",img)
    cv2.waitKey(1)
