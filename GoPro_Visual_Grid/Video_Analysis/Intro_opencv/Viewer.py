import numpy as np
import cv2

# What file are we loading?
Version = ''
Base_Name = '003_camera_p3'
Name_of_File = Base_Name + Version
format = '.avi'
fileName = Name_of_File + format

cap = cv2.VideoCapture(fileName)  # load the video
while (cap.isOpened()):  # play the video by reading frame by frame
    ret, frame = cap.read()
    if ret == True:
        # optional: do some image processing here

        cv2.imshow('frame', frame)  # show the video
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()