import numpy as np
import cv2
import time

color = (255, 0, 0)
thickness = 2

cap = cv2.VideoCapture(0)
while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()  # ret = 1 if the video is captured; frame is the image

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray,(21,21),0)
    ret, thresh = cv2.threshold(gray, 75, 100, cv2.THRESH_BINARY_INV)

    # cv2.findContours(image, mode, method[, contours[, hierarchy[, offset]]]) → contours, hierarchy

    # cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    img1, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        c = max(contours, key=cv2.contourArea)  # find the largest contour
        x, y, w, h = cv2.boundingRect(c)  # get bounding box of largest contour
        # img2=cv2.drawContours(frame, c, -1, color, thickness) # draw largest contour
        img2 = cv2.drawContours(frame, contours, -1, color, thickness)  # draw all contours
        img3 = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)  # draw red bounding box in img

    # Display the resulting image
    cv2.imshow('Contour', img2)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()