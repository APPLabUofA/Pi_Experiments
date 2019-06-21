import numpy as np
import cv2

kernelSize = 21  # Kernel Bluring size

# Edge Detection Parameter
parameter1 = 20
parameter2 = 60
intApertureSize = 1

cap = cv2.VideoCapture(0)
while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    frame = cv2.GaussianBlur(frame, (kernelSize, kernelSize), 0, 0)
    frame = cv2.Canny(frame, parameter1, parameter2, intApertureSize)  # Canny edge detection
    # frame = cv2.Laplacian(frame,cv2.CV_64F) # Laplacian edge detection
    # frame = cv2.Sobel(frame,cv2.CV_64F,1,0,ksize=kernelSize) # X-direction Sobel edge detection
    # frame = cv2.Sobel(frame,cv2.CV_64F,0,1,ksize=kernelSize) # Y-direction Sobel edge detection

    # Display the resulting frame
    cv2.imshow('Canny', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()