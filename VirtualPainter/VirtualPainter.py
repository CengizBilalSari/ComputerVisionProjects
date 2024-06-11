import cv2
import numpy as np
import time
import mediapipe as mp
import os
import HandTrackingModule as htm


# thickness of circle of brushes and the eraser
brush_thickness=15
eraser_thickness=80


#path of the control side of the image
folderPath= "Painter"
myList= os.listdir(folderPath)
overlayList=[]

for imPath in myList:
    image= cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)



header= overlayList[0]

# color of drawing  could be changed, initially it is pink
drawColor= (255,0,255)


# open cam
cap= cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

fps= 30

cap.set(5,fps)
#hand detector
detector= htm.handDetector(min_detection_confidence=0.85)


# these booleans are created for changing the color of brush
is_blue=False
is_pink=False
is_green=False
is_eraser=False

xp,yp=0,0  # they are used for drawing constantly

# first draw on canvas and then program will overlap them.
imgCanvas= np.zeros((720,1280,3),np.uint8)


while True:
    # import image
    success,img= cap.read()

    # 2. Find Hand Landmarks
    img=detector.findHands(img,draw=False)
    lmList= detector.findPosition(img,draw=False)

    if len(lmList)!=0:


        # tip of index and middle fingers
        x1,y1= lmList[8][1:]
        x2,y2= lmList[12][1:]


    # 3. Check which fingers are up
        fingers =detector.fingersUp()

    #4. If  selection mode- two finger are up
        if fingers[1]and fingers[2]:
            xp, yp = 0, 0
            # check the which color will be used
            if y1<125:
                #checking for the click
                if 233<x1<320:
                    is_pink=True
                    is_blue, is_eraser, is_green = False, False, False
                    drawColor= (255, 0, 255)
                elif 555<x1<650:
                    is_green=True
                    is_pink, is_blue, is_eraser = False, False, False
                    drawColor = (0,255, 0)
                elif  800<x1<890:
                    is_blue=True
                    is_eraser, is_green, is_pink = False, False, False
                    drawColor = (255,0,0)
                elif 1080<x1<1240:
                    is_eraser=True
                    is_pink, is_blue, is_green = False, False, False
                    drawColor=(0,0,0)
            if is_pink:
                cv2.putText(img, "PINK", (35, 180), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 4)
            elif is_green:
                cv2.putText(img, "GREEN", (35, 180), cv2.FONT_HERSHEY_PLAIN, 4, (0, 255, 0), 4)
            elif is_blue:
                cv2.putText(img, "BLUE", (35, 180), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)
            elif is_eraser:
                cv2.putText(img, "ERASER", (35, 180), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)

            # when user up his two finger for selection mode, there is a rectangle for selection
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor,cv2.FILLED)
    #5. If  drawing mode- one finger is up
        if fingers[1] and fingers[2] == False:
            # draw with circle sign
            cv2.circle(img,(x1,y1),15,drawColor,cv2.FILLED)

            if(xp==0 and yp==0):  # for problem of beginning
                xp,yp=x1,y1

            # eraser
            if drawColor==(0,0,0):
                #If the selected color is black (eraser), it uses cv2.line to draw a black line with the specified eraser thickness.
                # This line erases the drawn content by making the corresponding pixels black in both the main image (img)
                # and the canvas (imgCanvas).
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraser_thickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraser_thickness)
            # other preferences
            else:
                #The drawn line is also replicated on the canvas (imgCanvas) to keep track of the drawing.

                cv2.line(img,(xp,yp),(x1,y1),drawColor,brush_thickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness)
            xp,yp=x1,y1

    # These part is for overlapping canvas and the main program etc.
    img_gray= cv2.cvtColor(imgCanvas,cv2.COLOR_BGR2GRAY)
    _, img_inv= cv2.threshold(img_gray,50,255,cv2.THRESH_BINARY_INV)
    img_inv=cv2.cvtColor(img_inv,cv2.COLOR_GRAY2BGR)

    #to combine the img and canvas img

    #Program does this by creating a mask from the canvas, inverting it, and then applying it to the main image.
    # This way, the drawings on the canvas are overlaid onto the main image.
    img = cv2.bitwise_and(img,img_inv)
    img= cv2.bitwise_or(img,imgCanvas)


    #setting the header image( control panel
    img[0:125,0:1278]= header
    #img[0:122,0:1280]=header
    #img= cv2.addWeighted(img,0.5,imgCanvas,0.5,0)

    cv2.imshow("Image",img)
    cv2.imshow("Canvas", imgCanvas)
    cv2.waitKey(1)
