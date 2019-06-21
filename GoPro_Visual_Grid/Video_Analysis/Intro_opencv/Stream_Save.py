import numpy as np
import cv2

# create writer object
fileName='output0001.avi'  # change the file name if needed
imgSize=(640,480)
frame_per_second=30.0
writer = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(*"MJPG"), frame_per_second,imgSize)

cap = cv2.VideoCapture(0)
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        writer.write(frame)                   # save the frame into video file
        cv2.imshow('Video Capture',frame)     # show on the screen
        if cv2.waitKey(25) & 0xFF == ord('q'): # press q to quit
            break
    else:
        break

# Release everything if job is finished
cap.release()
writer.release()
cv2.destroyAllWindows()