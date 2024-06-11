import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self,mode=False, max_num_hands= 2,model_complexity=1,min_detection_confidence=0.5,min_tracking_confidence=0.5): # confidences are degree of certainty,
        # if degree decreases to below of this value, detection or tracking is reproducing again.
        self.mode=mode
        self.max_num_hands= max_num_hands
        self.model_complexity=model_complexity
        self.min_detection_confidence= min_detection_confidence
        self.min_tracking_confidence=min_tracking_confidence

        self.mpHands= mp.solutions.hands
        self.hands= self.mpHands.Hands(self.mode,self.max_num_hands,self.model_complexity,self.min_detection_confidence,min_tracking_confidence) # there are default parameters in Hands function
        self.mpDraw= mp.solutions.drawing_utils

        self.tip_ids= [4,8,12,16,20];

    def findHands(self,img,draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # This class just use RGB, so convert it to converge RGB
        self.results = self.hands.process(imgRGB)
        # extract multiple hands and check them with for loop
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:  # if there are hands, draw their connections
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,
                                           landmark_drawing_spec=self.mpDraw.DrawingSpec(color=(255, 0, 0)))

        return img

    def findPosition(self,img,handNumber=0,draw=True):
        self.landmark_list=[]  #for one particular hand
        if self.results.multi_hand_landmarks:  # if there are hands
            my_hand= self.results.multi_hand_landmarks[handNumber]
            for id, landmark in enumerate(my_hand.landmark):  # id of exact number of finger landmark
            #we are going to use x,y coordinates to find the location of the landmark on the hand
                height, width, channel = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                self.landmark_list.append([id,cx,cy])
                if draw:   # custom drawing
                    cv2.circle(img, (cx, cy), 10, (255,0,0), cv2.FILLED)
        return self.landmark_list


    def findPosition_bbox(self,img,handNumber=0,draw=True):

        x_list= []
        y_list=[]
        bbox=[]
        self.landmark_list=[]  #for one particular hand

        if self.results.multi_hand_landmarks:  # if there are hands
            my_hand= self.results.multi_hand_landmarks[handNumber]
            for id, landmark in enumerate(my_hand.landmark):  # id of exact number of finger landmark
            #we are going to use x,y coordinates to find the location of the landmark on the hand
                height, width, channel = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                x_list.append(cx)
                y_list.append(cy)
                self.landmark_list.append([id,cx,cy])
                if draw:   # custom drawing
                    cv2.circle(img, (cx, cy), 10, (255,0,0), cv2.FILLED)

            xmin,xmax= min(x_list),max(x_list)
            ymin,ymax= min(y_list),max(y_list)
            bbox= xmin,ymin,xmax,ymax

            if draw:
                    cv2.rectangle(img,(xmin-20,ymin-20),(xmax+20,ymax+20,),(0,255,0),2)

        return self.landmark_list,bbox
    def fingersUp(self):
        fingers = []
        # for thumb we have to check it  separately, is it in the left side of  the below one
        if self.landmark_list[self.tip_ids[0]][1] > self.landmark_list[self.tip_ids[0] - 1][1]:  # up is lower values
            fingers.append(1)
        else:
            fingers.append(0)

        # other four fingers
        for number in range(1, 5):
            if self.landmark_list[self.tip_ids[number]][2] < self.landmark_list[self.tip_ids[number] - 2][2]:  # up is lower values
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
def main():
    previousTime=0
    currentTime=0
    cap = cv2.VideoCapture(0)  # video capture
    detector= handDetector()
    while True:
        success,img=cap.read()  # get image
        img= detector.findHands(img)
        landmark_list= detector.findPosition(img)
        if len(landmark_list)!=0:
            print(landmark_list[4])  #thumb

        # to calculate fps for image
        currentTime = time.time()
        fps = 1 / (currentTime - previousTime)
        previousTime = currentTime

        # put the fps information to screen
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__== "__main__":
    main()