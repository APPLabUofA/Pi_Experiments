import numpy as np
import cv2
import time
import rpi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.warning(False)

pin = 18
color = (255, 0, 0)
thickness = 2

count = 0

### Change video input
cap = cv2.VideoCapture(0)
while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()  # ret = 1 if the video is captured; frame is the image

    if GPIO.input(pin) == GPIO.HIGH:
	GPIO.output(pin, GPIO.LOW)


    if count % 24 == 0:
	GPIO.output(pin, GPIO.HIGH)
    
    count += 1	

    # Display the resulting image
    cv2.imshow('Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
