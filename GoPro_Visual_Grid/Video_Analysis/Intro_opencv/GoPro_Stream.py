import cv2
import numpy as np
from goprocam import GoProCamera
from goprocam import constants
cascPath="/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
gpCam = GoProCamera.GoPro()
cap = cv2.VideoCapture("udp://127.0.0.1:10000")
while True:
    ret, frame = cap.read()
    if ret == True:

        # gray = cv2.cvtColor(frame, 0)
        #
        cv2.imshow("GoPro OpenCV", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()