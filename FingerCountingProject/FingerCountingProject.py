import cv2
import time
import os
import HandTrackingModule as htm

cap= cv2.VideoCapture(0)

#####################
wCam,hCam= 1280,720
#####################

folder_path="Fingers"
my_list= os.listdir(folder_path)
print(my_list)
overlay_list=[]
for im_path in my_list:
    image= cv2.imread(f'{folder_path}/{im_path}')
    overlay_list.append(image)


previous_time=0
detector= htm.handDetector(min_detection_confidence=0.75)
tip_ids= [4,8,12,16,20]

while True:
    success,img=cap.read()  #get image h,w,c= overlay_list[0].shape
    img = detector.findHands(img)
    lm_list= detector.findPosition(img,draw=False)

    if len(lm_list)!=0:
        fingers=[]
        #for thumb we have to check it  separately, is it in the left side of  the below one
        if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:  # up is lower values
            fingers.append(1)
        else:
            fingers.append(0)

        #other four fingers
        for  number in range(1,5):
            if lm_list[tip_ids[number]][2]< lm_list[tip_ids[number]-2][2]:  # up is lower values
                fingers.append(1)
            else:
                fingers.append(0)
        #print(fingers)
        totalFingers= fingers.count(1)

        h, w, c = overlay_list[totalFingers-1].shape
        img[0:h, 0:w] = overlay_list[totalFingers-1]  # place sample picture into original image
        cv2.rectangle(img,(20,225),(170,425),(0,255,0),cv2.FILLED)
        cv2.putText(img,str(totalFingers),(45,375),cv2.FONT_HERSHEY_PLAIN,10,(255,0,0),25)
   

    current_time= time.time()
    fps= 1/(current_time-previous_time)
    previous_time=current_time

    cv2.putText(img,f'FPS: {int(fps)}',(400,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    cv2.imshow("Image",img)
    cv2.waitKey(1) # 1 ms delay to see image
