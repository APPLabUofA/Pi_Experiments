import numpy as np
import cv2
import time

color = (255, 0, 0)
thickness = 2

cap = cv2.VideoCapture(0)
while (True):
    # Capture two frames
    ret, frame1 = cap.read()  # first image
    time.sleep(1 / 25)  # slight delay
    ret, frame2 = cap.read()  # second image
    img1 = cv2.absdiff(frame1, frame2)  # image difference

    # get theshold image
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    ret, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_OTSU)

    # combine frame and the image difference
    img2 = cv2.addWeighted(frame1, 0.9, img1, 0.1, 0)

    # get contours and set bounding box from contours
    img3, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        for c in contours:
            rect = cv2.boundingRect(c)
            height, width = img3.shape[:2]
            if rect[2] > 0.2 * height and rect[2] < 0.7 * height and rect[3] > 0.2 * width and rect[3] < 0.7 * width:
                x, y, w, h = cv2.boundingRect(c)  # get bounding box of largest contour
                img4 = cv2.drawContours(img2, c, -1, color, thickness)
                img5 = cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)  # draw red bounding box in img
            else:
                img5 = img2
    else:
        img5 = img2

    # Display the resulting image
    cv2.imshow('Motion Detection by Image Difference', img2)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()